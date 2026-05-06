#!/usr/bin/env python3
"""
Compass Wiki Sync — 飞书 Wiki 文档拉取与同步流水线

功能：
1. 读取 config/sources.yaml 中的 wiki 节点配置
2. 拉取 docx 类型的 Wiki 文档到 workspace/raw_lark/wiki/
3. 为每篇文档添加/补全 frontmatter（lark_url, lark_node_id, scope, project_id）
4. 计算 content_hash，与 sync_state.json 对比，仅同步变更文档
5. 可选：自动触发 wiki_ingest.py 进行知识编译

Usage:
    python tools/wiki_sync.py --all                # 全量同步所有配置的 docx 节点
    python tools/wiki_sync.py --node=<node_token>  # 同步单个 Wiki 节点
    python tools/wiki_sync.py --all --ingest       # 同步后自动 ingest
    python tools/wiki_sync.py --dry-run            # 模拟运行，不写入文件

注意：
- 目前 sources.yaml 中的 nodes 均为 bitable（Base）入口，docx 节点需手动添加
- 对于 folder 类型的节点，会尝试递归列出子节点（需要 Wiki 空间读取权限）
"""

import os
import sys
import re
import json
import hashlib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from datetime import datetime

# 路径常量（基于 workspace 目录结构）
# tools/ -> agents/wiki-manager/workspace/
WORKSPACE = Path(__file__).resolve().parent.parent
CONFIG_FILE = WORKSPACE / "config" / "sources.yaml"
STATE_DIR = WORKSPACE / "state"
SYNC_STATE_FILE = STATE_DIR / "sync_state.json"
RAW_LARK_WIKI_DIR = WORKSPACE / "raw_lark" / "wiki"

def load_sources_config() -> dict:
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML not installed. Run: pip install pyyaml")
        sys.exit(1)
    return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}

def run_lark_cli(*args) -> dict:
    """运行 lark-cli 命令，优先使用 user 身份，如果没有用户登录则回退到 bot"""
    # 首先尝试使用 user 身份
    cmd_user = ["lark-cli"] + list(args) + ["--profile=compass", "--as", "user"]
    result = subprocess.run(cmd_user, capture_output=True, text=True)
    
    # 如果失败且是因为没有用户登录，则回退到 bot 身份
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        
        # 检查是否是用户未登录的错误
        if ("need_user_authorization" in stderr or 
            "need_user_authorization" in stdout or
            "No user logged in" in stderr or
            "No user logged in" in stdout):
            print(f"   ⚠️  User not logged in, falling back to bot identity")
            cmd_bot = ["lark-cli"] + list(args) + ["--profile=compass", "--as", "bot"]
            result = subprocess.run(cmd_bot, capture_output=True, text=True)
        elif stderr:
            print(f"   lark-cli stderr: {stderr[:200]}")
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "Invalid JSON", "raw": result.stdout[:500]}

def is_ok(resp: dict) -> bool:
    return resp.get("ok") or resp.get("code") == 0

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]

# ── Lark Table 转换 ──────────────────────────────────────────────

def convert_lark_tables(content: str) -> str:
    """将 <lark-table> XML 块转换为 markdown pipe tables

    飞书导出的表格使用 <lark-table><lark-tr><lark-td> 的 XML 格式，
    对 LLM 极不友好（token 开销大 5-10 倍）。在 sync 阶段就转换为标准
    markdown pipe table，可显著降低后续 ingest 的 token 消耗。
    """
    result = []
    i = 0
    while True:
        start = content.find('<lark-table', i)
        if start == -1:
            result.append(content[i:])
            break

        result.append(content[i:start])
        end = content.find('</lark-table>', start)
        if end == -1:
            result.append(content[start:])
            break

        end += len('</lark-table>')
        xml_block = content[start:end]

        try:
            table_md = _lark_table_to_markdown(xml_block)
            result.append(table_md)
        except Exception:
            # 转换失败时保留原 XML，避免丢失数据
            result.append(xml_block)

        i = end

    return ''.join(result)


def _lark_table_to_markdown(xml_block: str) -> str:
    """用正则提取 lark-tr / lark-td，避免 XML 解析器对 cell 内 `<` 字符报错"""
    rows = []
    for tr_match in re.finditer(r'<lark-tr>\s*(.*?)\s*</lark-tr>', xml_block, re.DOTALL):
        tr_content = tr_match.group(1)
        cells = []
        for td_match in re.finditer(r'<lark-td>\s*(.*?)\s*</lark-td>', tr_content, re.DOTALL):
            text = td_match.group(1).strip()
            text = text.replace('|', '\\|').replace('\n', ' ')
            cells.append(text)
        if cells:
            rows.append(cells)

    if not rows:
        return ''

    col_count = max(len(r) for r in rows)
    lines = []
    header = rows[0] + [''] * (col_count - len(rows[0]))
    lines.append('| ' + ' | '.join(header) + ' |')
    lines.append('|' + '|'.join([' --- '] * col_count) + '|')
    for row in rows[1:]:
        row = row + [''] * (col_count - len(row))
        lines.append('| ' + ' | '.join(row[:col_count]) + ' |')

    return '\n'.join(lines)


# ── 文档类型检测 ─────────────────────────────────────────────────

def detect_doc_type(title: str, content: str, rel_path: str) -> str:
    """根据标题、正文和路径自动判定文档类型

    优先级：路径关键字 > 标题关键字 > 正文结构匹配
    """
    title_lower = title.lower()
    path_lower = rel_path.lower()
    content_preview = content[:3000].lower()

    # 1. 路径关键字（最高置信度）
    if '周报归档' in path_lower:
        if '部门' in title or 'mcn事业部' in title_lower:
            return 'dept-weekly'
        return 'project-weekly'
    if '会议纪要' in path_lower:
        return 'meeting'
    if '项目文档' in path_lower:
        return 'project-doc'

    # 2. 标题关键字
    if '部门周报' in title:
        return 'dept-weekly'
    if 'week' in title_lower and '周报' in title:
        return 'project-weekly'
    if '会议纪要' in title or '会议' in title:
        if '基本信息' in content and ('讨论要点' in content or '决策' in content):
            return 'meeting'
    if 'onepage' in title_lower or 'one page' in title_lower:
        if '部门' in title_lower or '事业部' in title_lower:
            return 'dept-onepage'
        return 'project-onepage'
    if any(k in title for k in ['手册', 'sop', '规范', '方案', '报告', '模板']):
        return 'project-doc'

    # 3. 正文结构匹配（兜底）
    has_data_board = '数据看板' in content_preview or '本周数据' in content_preview
    has_tasks = '任务完成情况' in content_preview
    has_risks = '风险与阻塞' in content_preview
    has_kpi = '核心kpi' in content_preview or 'kpi' in content_preview
    has_threshold = '风险阈值' in content_preview
    has_agenda = '会议议程' in content_preview or '讨论要点' in content_preview
    has_todo = '行动项' in content_preview or 'todo' in content_preview

    if has_data_board and has_tasks and has_risks:
        if '部门' in title or 'mcn' in title_lower:
            return 'dept-weekly'
        return 'project-weekly'
    if has_agenda and has_todo:
        return 'meeting'
    if has_kpi and has_threshold:
        if '部门' in title_lower:
            return 'dept-onepage'
        return 'project-onepage'
    if '输出背景' in content_preview:
        return 'project-doc'

    return 'default'


# ── 内容清理 ─────────────────────────────────────────────────────

def remove_feishu_footer(content: str) -> str:
    """移除文末冗余的"飞书 Wiki 在线地址"脚注

    该信息已包含在 frontmatter 的 lark_url 中，正文中保留会造成重复。
    """
    # 匹配 "---\n\n**飞书 Wiki 在线地址**：..." 到文末
    footer_pattern = r'\n---\n\n\*\*飞书 Wiki 在线地址\*\*：.*?\n?$'
    cleaned = re.sub(footer_pattern, '', content, flags=re.DOTALL)
    return cleaned


def load_sync_state() -> dict:
    if SYNC_STATE_FILE.exists():
        return json.loads(SYNC_STATE_FILE.read_text(encoding="utf-8"))
    return {
        "last_full_sync_at": None,
        "last_incremental_check_at": None,
        "pending_changes": 0,
        "is_syncing": False,
        "sync_version": 1,
        "sources": {"wiki": {"count": 0, "items": []}, "base": {"count": 0, "items": []}}
    }

def save_sync_state(state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def extract_frontmatter(content: str) -> tuple[dict, str]:
    import re
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if match:
        fm_text, body = match.group(1), match.group(2)
        try:
            import yaml
            return yaml.safe_load(fm_text) or {}, body
        except ImportError:
            return {}, content
    return {}, content

def build_frontmatter(metadata: dict) -> str:
    try:
        import yaml
    except ImportError:
        return ""
    lines = yaml.dump(metadata, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{lines}\n---\n\n"

def fetch_wiki_doc(node_token: str, node_title: str = "", obj_token: str = "") -> tuple[str | None, str | None]:
    """拉取 Wiki 文档内容（docx）

    优先使用 obj_token（真实文档 ID），否则回退到 node_token 或 wiki URL。
    返回 (content, error_type)：
        - content 为文档内容，error_type 为 None → 成功
        - content 为 None，error_type 为 'not_found' → 文档在飞书侧已删除/不可见
        - content 为 None，error_type 为 'fetch_failed' → 网络/权限等其他错误
    """
    doc_id = obj_token or node_token
    print(f"   Fetching doc content for {doc_id}...")

    # Strategy 1: fetch with obj_token (preferred)
    resp = run_lark_cli("docs", "+fetch", f"--doc={doc_id}", "--format=json")
    if is_ok(resp) and resp.get("data"):
        data = resp.get("data", {})
        content = data.get("markdown", "") or data.get("content", "")
        if not content and "blocks" in data:
            content = blocks_to_markdown(data["blocks"])
        if content:
            return content, None

    # Strategy 2: try with full wiki URL
    wiki_url = f"https://ncnkdep1f4r7.feishu.cn/wiki/{node_token}"
    resp2 = run_lark_cli("docs", "+fetch", f"--doc={wiki_url}", "--format=json")
    if is_ok(resp2) and resp2.get("data"):
        data = resp2.get("data", {})
        content = data.get("markdown", "") or data.get("content", "")
        if not content and "blocks" in data:
            content = blocks_to_markdown(data["blocks"])
        if content:
            return content, None

    # Determine error type
    err_msg = ""
    for r in (resp, resp2):
        if r and not is_ok(r):
            err = r.get("error", {})
            if isinstance(err, dict):
                err_msg = err.get("message", "")
            elif isinstance(err, str):
                err_msg = err
            raw = r.get("raw", "")
            if not err_msg:
                err_msg = raw
            break

    err_lower = err_msg.lower()
    if any(k in err_lower for k in ("404", "not found", "不存在", "无法访问", "no permission to view")):
        print(f"   ⚠️  Document not found or no access (archiving): {node_token}")
        return None, "not_found"

    print(f"   ⚠️  Failed to fetch content for {node_token}: {err_msg[:120]}")
    return None, "fetch_failed"

def blocks_to_markdown(blocks: list) -> str:
    """将飞书 docx block 列表转换为 Markdown（简化版）"""
    lines = []
    for block in blocks:
        btype = block.get("type", "")
        text = ""
        if "text" in block:
            text = block["text"]
        elif "elements" in block:
            for elem in block["elements"]:
                text += elem.get("text", "")

        if btype == "heading1":
            lines.append(f"# {text}")
        elif btype == "heading2":
            lines.append(f"## {text}")
        elif btype == "heading3":
            lines.append(f"### {text}")
        elif btype == "bullet":
            lines.append(f"- {text}")
        elif btype == "ordered":
            lines.append(f"1. {text}")
        elif btype == "code":
            lines.append(f"```\n{text}\n```")
        elif btype == "quote":
            lines.append(f"> {text}")
        else:
            if text:
                lines.append(text)
    return "\n\n".join(lines)


# ── 增量同步相关函数 ────────────────────────────────────────────

def get_all_wiki_nodes(space_id: str) -> list[dict]:
    """获取 Wiki 空间中的所有节点（处理分页）
    
    飞书 API 每次最多返回 50 个节点，需要分页获取所有节点。
    """
    all_items = []
    page_token = ""
    page_count = 0
    max_pages = 10  # 安全限制，最多获取 10 页
    
    while page_count < max_pages:
        params = {"space_id": space_id}
        if page_token:
            params["page_token"] = page_token
        
        resp = run_lark_cli("wiki", "nodes", "list", "--params", json.dumps(params))
        if not is_ok(resp) or not resp.get("data"):
            break
        
        data = resp.get("data", {})
        items = data.get("items", [])
        all_items.extend(items)
        
        page_count += 1
        print(f"   📄 Page {page_count}: {len(items)} nodes (total: {len(all_items)})")
        
        # 检查是否有更多页
        has_more = data.get("has_more", False)
        page_token = data.get("page_token", "")
        
        if not has_more or not page_token:
            break
    
    return all_items


def get_doc_metadata(node_token: str, obj_token: str = "", all_nodes: list[dict] = None) -> dict:
    """获取飞书文档元数据（修改时间等）
    
    使用预获取的节点列表或实时获取节点信息
    返回 {"last_modified_time": "2026-05-06T12:00:00Z", "obj_edit_time": 1777910631} 或 {}
    """
    # 如果提供了预获取的节点列表，直接查找
    if all_nodes:
        for item in all_nodes:
            if item.get("node_token") == node_token:
                obj_edit_time = item.get("obj_edit_time", 0)
                if obj_edit_time:
                    # 确保是整数
                    if isinstance(obj_edit_time, str):
                        obj_edit_time = int(obj_edit_time)
                    dt = datetime.fromtimestamp(obj_edit_time, tz=timezone.utc)
                    iso_time = dt.isoformat()
                else:
                    iso_time = ""
                    obj_edit_time = 0
                return {
                    "last_modified_time": iso_time,
                    "obj_edit_time": obj_edit_time,
                    "creator": item.get("creator", ""),
                }
        return {}
    
    # 回退：从配置中读取 space_id 并实时获取
    config = load_sources_config()
    space_id = config.get("wiki", {}).get("space", {}).get("space_id", "")
    
    if space_id:
        all_nodes = get_all_wiki_nodes(space_id)
        return get_doc_metadata(node_token, obj_token, all_nodes)
    
    return {}


def should_sync(node_config: dict, all_nodes: list[dict] = None) -> tuple[bool, str]:
    """判断文档是否需要同步
    
    返回 (needs_sync, reason)
    - needs_sync: True/False
    - reason: 原因说明
    """
    node_token = node_config["node_token"]
    title = node_config.get("title", "Untitled")
    scope = node_config.get("scope", "public")
    project_id = node_config.get("project_id")
    
    # 构建本地文件路径
    scope_dir = RAW_LARK_WIKI_DIR / scope
    if scope == "projects" and project_id:
        scope_dir = RAW_LARK_WIKI_DIR / "projects" / project_id
    safe_title = title.replace("/", "_").replace("\\", "_")[:80]
    output_path = scope_dir / f"{safe_title}.md"
    
    # 1. 检查本地文件是否存在
    if not output_path.exists():
        return True, "New document (not in local)"
    
    # 2. 读取本地 frontmatter
    old_content = output_path.read_text(encoding="utf-8")
    old_fm, old_body = extract_frontmatter(old_content)
    local_hash = old_fm.get("content_hash", "")
    local_status = old_fm.get("status", "active")
    local_fetched_at = old_fm.get("fetched_at", "")
    
    # 3. 如果本地文件被归档，检查是否需要恢复
    if local_status == "archived":
        return True, "Local file archived, checking if restored"
    
    # 4. 获取飞书文档元数据（使用预获取的节点列表）
    obj_token = node_config.get("obj_token", "")
    metadata = get_doc_metadata(node_token, obj_token, all_nodes)
    
    if not metadata:
        # 无法获取元数据，保守策略：同步
        return True, "Cannot fetch metadata, syncing to be safe"
    
    # 5. 对比修改时间
    feishu_modified = metadata.get("last_modified_time", "")
    if feishu_modified and local_fetched_at:
        try:
            # 解析时间字符串，确保都有时区信息
            feishu_time = datetime.fromisoformat(feishu_modified.replace("Z", "+00:00"))
            # 本地时间可能没有时区，添加 UTC 时区
            if local_fetched_at.endswith('Z'):
                local_time = datetime.fromisoformat(local_fetched_at.replace("Z", "+00:00"))
            elif '+' not in local_fetched_at and '-' not in local_fetched_at[-6:]:
                # 没有时区信息，假设是 UTC
                local_time = datetime.fromisoformat(local_fetched_at).replace(tzinfo=timezone.utc)
            else:
                local_time = datetime.fromisoformat(local_fetched_at)
            
            if feishu_time <= local_time:
                return False, f"No change (Feishu modified: {feishu_modified}, last synced: {local_fetched_at})"
            else:
                return True, f"Modified on Feishu ({feishu_modified} > {local_fetched_at})"
        except ValueError:
            # 时间解析失败，保守策略
            return True, "Time parse error, syncing to be safe"
    
    # 6. 没有时间信息，使用 hash 对比（需要拉取内容）
    return True, "No timestamp info, will compare hash"


def sync_node_incremental(node_config: dict, dry_run: bool = False, force: bool = False, all_nodes: list[dict] = None) -> dict:
    """增量同步单个 Wiki 节点
    
    1. 先检查元数据判断是否需要同步
    2. 只有需要同步时才拉取内容
    3. 对比 hash 确认变更
    """
    node_token = node_config["node_token"]
    title = node_config.get("title", "Untitled")
    scope = node_config.get("scope", "public")
    project_id = node_config.get("project_id")
    node_type = node_config.get("type", "docx")
    lark_url = node_config.get("lark_url", f"https://ncnkdep1f4r7.feishu.cn/wiki/{node_token}")

    print(f"\n📄 [{scope}] {title} ({node_token}, type={node_type})")

    if node_type == "bitable":
        print(f"   ⏭️  Skipping bitable node (handled by base_sync.py)")
        return {"status": "skipped", "reason": "bitable"}

    if node_type == "folder":
        print(f"   📁 Folder node — listing children not yet implemented (needs Wiki space read permission)")
        return {"status": "skipped", "reason": "folder"}

    # 1. 判断是否需要同步
    if not force and not dry_run:
        needs_sync, reason = should_sync(node_config, all_nodes)
        print(f"   🔍 {reason}")
        if not needs_sync:
            return {"status": "unchanged", "reason": reason}
    elif dry_run:
        print(f"   🧪 Dry run: would check metadata and sync if needed")
        return {"status": "dry_run"}
    else:
        print(f"   🔄 Force sync")

    # 2. 拉取内容（只有需要同步时才执行）
    obj_token = node_config.get("obj_token", "")
    raw_content, error_type = fetch_wiki_doc(node_token, title, obj_token)
    if raw_content is None:
        if error_type == "not_found":
            # 归档本地文件
            scope_dir = RAW_LARK_WIKI_DIR / scope
            if scope == "projects" and project_id:
                scope_dir = RAW_LARK_WIKI_DIR / "projects" / project_id
            safe_title = title.replace("/", "_").replace("\\", "_")[:80]
            output_path = scope_dir / f"{safe_title}.md"
            if output_path.exists():
                old_content = output_path.read_text(encoding="utf-8")
                old_fm, old_body = extract_frontmatter(old_content)
                old_fm["status"] = "archived"
                old_fm["archived_at"] = datetime.now().isoformat()
                old_fm["archive_reason"] = "Document deleted or moved on Feishu"
                full_content = build_frontmatter(old_fm) + old_body
                output_path.write_text(full_content, encoding="utf-8")
                print(f"   🗃️  Archived local file (doc deleted on Feishu)")
                return {
                    "status": "archived",
                    "path": str(output_path),
                    "hash": sha256_text(old_body),
                }
        return {"status": "error", "reason": error_type or "fetch_failed"}

    # 3. 预处理内容
    content = convert_lark_tables(raw_content)
    table_converted = content != raw_content
    content = remove_feishu_footer(content)
    body_hash = sha256_text(content)
    
    # 4. 构建输出路径
    scope_dir = RAW_LARK_WIKI_DIR / scope
    if scope == "projects" and project_id:
        scope_dir = RAW_LARK_WIKI_DIR / "projects" / project_id
    scope_dir.mkdir(parents=True, exist_ok=True)
    
    safe_title = title.replace("/", "_").replace("\\", "_")[:80]
    output_path = scope_dir / f"{safe_title}.md"
    
    # 5. 对比 hash（二次确认）
    if output_path.exists() and not force:
        old_content = output_path.read_text(encoding="utf-8")
        old_fm, old_body = extract_frontmatter(old_content)
        old_hash = old_fm.get("content_hash", "")
        if old_hash == body_hash:
            print(f"   ✅ No change (hash match: {body_hash[:8]})")
            # 更新时间戳但不标记为变更
            old_fm["fetched_at"] = datetime.now().isoformat()
            full_content = build_frontmatter(old_fm) + old_body
            output_path.write_text(full_content, encoding="utf-8")
            return {"status": "unchanged", "hash": body_hash}
        else:
            print(f"   ✏️  Modified (old: {old_hash[:8] if old_hash else 'none'}, new: {body_hash[:8]})")
    else:
        if output_path.exists():
            print(f"   🔄 Force sync (hash: {body_hash[:8]})")
        else:
            print(f"   🆕 New document (hash: {body_hash[:8]})")
        if table_converted:
            print(f"      📊 Lark tables converted to markdown")

    # 6. 写入文件
    doc_type = detect_doc_type(title, content, str(output_path.relative_to(RAW_LARK_WIKI_DIR)))
    
    fm = {
        "title": title,
        "doc_type": doc_type,
        "scope": scope,
        "lark_url": lark_url,
        "lark_node_id": node_token,
        "content_hash": body_hash,
        "fetched_at": datetime.now().isoformat(),
        "status": "active",
    }
    if project_id:
        fm["project_id"] = project_id

    full_content = build_frontmatter(fm) + content
    output_path.write_text(full_content, encoding="utf-8")
    print(f"   💾 Saved to {output_path}")

    return {
        "status": "synced",
        "path": str(output_path),
        "hash": body_hash,
    }

def sync_node(node_config: dict, dry_run: bool = False) -> dict:
    """同步单个 Wiki 节点"""
    node_token = node_config["node_token"]
    title = node_config.get("title", "Untitled")
    scope = node_config.get("scope", "public")
    project_id = node_config.get("project_id")
    node_type = node_config.get("type", "docx")
    lark_url = node_config.get("lark_url", f"https://ncnkdep1f4r7.feishu.cn/wiki/{node_token}")

    print(f"\n📄 [{scope}] {title} ({node_token}, type={node_type})")

    if node_type == "bitable":
        print(f"   ⏭️  Skipping bitable node (handled by base_sync.py)")
        return {"status": "skipped", "reason": "bitable"}

    if node_type == "folder":
        print(f"   📁 Folder node — listing children not yet implemented (needs Wiki space read permission)")
        return {"status": "skipped", "reason": "folder"}

    if dry_run:
        print(f"   🧪 Dry run: would fetch doc content")
        return {"status": "dry_run"}

    # Fetch content
    obj_token = node_config.get("obj_token", "")
    raw_content, error_type = fetch_wiki_doc(node_token, title, obj_token)
    if raw_content is None:
        if error_type == "not_found":
            # Archive local file if it exists
            scope_dir = RAW_LARK_WIKI_DIR / scope
            if scope == "projects" and project_id:
                scope_dir = RAW_LARK_WIKI_DIR / "projects" / project_id
            safe_title = title.replace("/", "_").replace("\\", "_")[:80]
            output_path = scope_dir / f"{safe_title}.md"
            if output_path.exists():
                old_content = output_path.read_text(encoding="utf-8")
                old_fm, old_body = extract_frontmatter(old_content)
                old_fm["status"] = "archived"
                old_fm["archived_at"] = datetime.now().isoformat()
                old_fm["archive_reason"] = "Document deleted or moved on Feishu"
                full_content = build_frontmatter(old_fm) + old_body
                output_path.write_text(full_content, encoding="utf-8")
                print(f"   🗃️  Archived local file (doc deleted on Feishu)")
                return {
                    "status": "archived",
                    "path": str(output_path),
                    "hash": sha256_text(old_body),
                }
        return {"status": "error", "reason": error_type or "fetch_failed"}

    # ── 预处理流水线（在写入 raw_lark 前完成所有格式清洗）──
    # 1. 转换 lark-table XML → markdown pipe table
    content = convert_lark_tables(raw_content)
    table_converted = content != raw_content
    # 2. 移除冗余的飞书脚注
    content = remove_feishu_footer(content)

    # Build output path
    scope_dir = RAW_LARK_WIKI_DIR / scope
    if scope == "projects" and project_id:
        scope_dir = RAW_LARK_WIKI_DIR / "projects" / project_id
    scope_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_title = title.replace("/", "_").replace("\\", "_")[:80]
    filename = f"{safe_title}.md"
    output_path = scope_dir / filename
    rel_path = str(output_path.relative_to(RAW_LARK_WIKI_DIR))

    # 3. 自动判定文档类型（基于路径 + 标题 + 正文结构）
    doc_type = detect_doc_type(title, content, rel_path)

    # Build clean frontmatter（仅保留"来源元数据"，去除 wiki 运行时状态字段）
    body_hash = sha256_text(content)
    fm = {
        "title": title,
        "doc_type": doc_type,
        "scope": scope,
        "lark_url": lark_url,
        "lark_node_id": node_token,
        "content_hash": body_hash,
        "fetched_at": datetime.now().isoformat(),
        "status": "active",
    }
    if project_id:
        fm["project_id"] = project_id

    # Check if file exists and compare hash
    if output_path.exists():
        old_content = output_path.read_text(encoding="utf-8")
        old_fm, old_body = extract_frontmatter(old_content)
        # Compare body content only (frontmatter may change with timestamps)
        old_hash = sha256_text(old_body)
        new_hash = sha256_text(content)
        if old_hash == new_hash:
            print(f"   ✅ No change (hash: {new_hash[:8]})")
            return {"status": "unchanged", "hash": new_hash}
        else:
            print(f"   ✏️  Modified (old: {old_hash[:8]}, new: {new_hash[:8]})")
    else:
        print(f"   🆕 New document (doc_type={doc_type})")
        if table_converted:
            print(f"      📊 Lark tables converted to markdown")

    # Write file with frontmatter
    full_content = build_frontmatter(fm) + content
    output_path.write_text(full_content, encoding="utf-8")
    print(f"   💾 Saved to {output_path}")

    return {
        "status": "synced",
        "path": str(output_path),
        "hash": new_hash if output_path.exists() else sha256_text(content),
    }

def update_sync_state_for_wiki(state: dict, node_token: str, result: dict):
    """更新 Wiki 节点的同步状态"""
    now = datetime.now().isoformat()
    items = state["sources"]["wiki"]["items"]

    existing = None
    for item in items:
        if item.get("lark_node_id") == node_token:
            existing = item
            break

    status_map = {
        "synced": "active",
        "unchanged": "active",
        "archived": "archived",
    }
    if existing:
        existing["content_hash"] = result.get("hash", "")
        existing["revision"] = result.get("revision", 1)
        existing["last_synced_at"] = now
        existing["status"] = status_map.get(result["status"], "error")
    else:
        items.append({
            "lark_node_id": node_token,
            "content_hash": result.get("hash", ""),
            "revision": result.get("revision", 1),
            "last_synced_at": now,
            "status": status_map.get(result["status"], "error"),
        })

    state["sources"]["wiki"]["count"] = len(items)
    return state

def main():
    parser = argparse.ArgumentParser(description="Sync Feishu Wiki docs to raw_lark/")
    parser.add_argument("--all", action="store_true", help="Sync all configured docx nodes")
    parser.add_argument("--node", default=None, help="Sync specific node by token")
    parser.add_argument("--ingest", action="store_true", help="Auto-trigger wiki_ingest.py after sync")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing files")
    parser.add_argument("--incremental", action="store_true", help="Incremental sync: only sync changed docs (default)")
    parser.add_argument("--force", action="store_true", help="Force sync all docs, ignore metadata/hash check")
    args = parser.parse_args()

    if not args.all and not args.node:
        parser.print_help()
        print("\nHint: Add docx nodes to config/sources.yaml under wiki.nodes to use --all")
        sys.exit(1)

    config = load_sources_config()
    nodes = config.get("wiki", {}).get("nodes", [])

    # Filter docx nodes
    docx_nodes = [n for n in nodes if n.get("type") in ("docx", "document", "wiki")]

    if args.node:
        # Sync specific node
        target = None
        for n in nodes:
            if n.get("node_token") == args.node:
                target = n
                break
        if not target:
            print(f"Error: Node {args.node} not found in config/sources.yaml")
            sys.exit(1)
        docx_nodes = [target]

    if not docx_nodes:
        print("=" * 60)
        print("Wiki Sync")
        print("=" * 60)
        print("\n⚠️  No docx nodes found in config/sources.yaml")
        print("\nCurrently configured nodes are all bitable (Base) entries.")
        print("To sync Wiki documents, add docx nodes like this to sources.yaml:")
        print("""
  nodes:
    - node_token: "YOUR_DOCX_NODE_TOKEN"
      title: "SOP/入职指南"
      scope: "public"
      type: "docx"
      lark_url: "https://ncnkdep1f4r7.feishu.cn/wiki/YOUR_DOCX_NODE_TOKEN"
""")
        sys.exit(0)

    print("=" * 60)
    print("Wiki Sync")
    print(f"Nodes to sync: {len(docx_nodes)}")
    print(f"Mode: {'dry-run' if args.dry_run else ('incremental' if not args.force else 'force')}")
    print("=" * 60)

    # 预获取所有飞书节点元数据（用于增量同步）
    all_nodes = None
    if not args.force and not args.dry_run:
        config = load_sources_config()
        space_id = config.get("wiki", {}).get("space", {}).get("space_id", "")
        if space_id:
            print(f"\n📡 Fetching metadata from Feishu (space_id: {space_id})...")
            all_nodes = get_all_wiki_nodes(space_id)
            print(f"   Found {len(all_nodes)} nodes on Feishu")

    state = load_sync_state()
    state["is_syncing"] = True
    save_sync_state(state)

    results = []
    synced_files = []
    archived_files = []
    try:
        for node in docx_nodes:
            # 使用增量同步（默认）或强制同步
            if args.force:
                result = sync_node(node, dry_run=args.dry_run)
            else:
                result = sync_node_incremental(node, dry_run=args.dry_run, all_nodes=all_nodes)
            result["node_token"] = node["node_token"]
            results.append(result)

            if result["status"] in ("synced", "unchanged"):
                state = update_sync_state_for_wiki(state, node["node_token"], result)
                if result["status"] == "synced":
                    synced_files.append(result["path"])
            elif result["status"] == "archived":
                state = update_sync_state_for_wiki(state, node["node_token"], result)
                archived_files.append(result["path"])

        state["last_full_sync_at"] = datetime.now().isoformat()
        state["is_syncing"] = False
        save_sync_state(state)

        # Summary
        print(f"\n{'='*60}")
        print("Summary")
        print(f"{'='*60}")
        synced_count = sum(1 for r in results if r["status"] == "synced")
        unchanged_count = sum(1 for r in results if r["status"] == "unchanged")
        skipped_count = sum(1 for r in results if r["status"] == "skipped")
        error_count = sum(1 for r in results if r["status"] == "error")
        archived_count = sum(1 for r in results if r["status"] == "archived")
        print(f"  Synced  : {synced_count}")
        print(f"  Unchanged: {unchanged_count}")
        print(f"  Skipped : {skipped_count}")
        print(f"  Archived: {archived_count}")
        print(f"  Errors  : {error_count}")
        print(f"  State   : {SYNC_STATE_FILE}")

        # Machine-readable footer for scheduler consumption
        print(f"__SYNC_REPORT__={json.dumps({'synced_files': synced_files, 'archived_files': archived_files}, ensure_ascii=False)}__")

        # Auto ingest
        if args.ingest and synced_files and not args.dry_run:
            print(f"\n🚀 Auto-triggering ingest for {len(synced_files)} files...")
            ingest_script = AGENT_DIR / "tools" / "wiki_ingest.py"
            for fpath in synced_files:
                full_path = Path(fpath)
                if not full_path.is_absolute():
                    full_path = AGENT_DIR / fpath
                if full_path.exists():
                    print(f"\n  Ingesting {fpath}...")
                    subprocess.run([sys.executable, str(ingest_script), str(full_path)])

    except KeyboardInterrupt:
        print("\nInterrupted.")
        state["is_syncing"] = False
        save_sync_state(state)
        sys.exit(1)

if __name__ == "__main__":
    main()
