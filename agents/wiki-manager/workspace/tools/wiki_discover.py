#!/usr/bin/env python3
"""
Wiki Discover — 自动扫描飞书 Wiki 空间，发现新文档并更新 sources.yaml

作为 wiki-sync 的前置步骤运行：
- 递归遍历飞书 Wiki 空间所有节点
- 对比 sources.yaml 中已注册的节点
- 自动 append 新增 docx 节点（按 scope_rules 推断 scope）
- title/obj_token 变更自动更新
- 飞书缺失的节点只输出告警，不删除

Usage:
    python tools/wiki_discover.py              # 执行发现并更新 sources.yaml
    python tools/wiki_discover.py --dry-run    # 预览变更，不写入
    python tools/wiki_discover.py --report     # 生成 state/discover_report.json
"""

from __future__ import annotations
import json
import re
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# tools/ -> workspace/ -> agents/wiki-manager/ -> agents/ -> repo_root/
def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

REPO_ROOT = _find_repo_root()
AGENT_WORKSPACE = REPO_ROOT / "agents" / "wiki-manager" / "workspace"
CONFIG_DIR = AGENT_WORKSPACE / "config"
SOURCES_YAML = CONFIG_DIR / "sources.yaml"
STATE_DIR = AGENT_WORKSPACE / "state"
DISCOVER_REPORT = STATE_DIR / "discover_report.json"


def run_lark_cli(cmd_args: list[str]) -> dict:
    """运行 lark-cli 命令并解析 JSON 输出（使用司南应用身份）"""
    try:
        result = subprocess.run(
            ["lark-cli", "--profile", "compass", "--as", "user"] + cmd_args,
            capture_output=True,
            text=True,
            check=True,
        )
        # 直接解析整个 stdout（多行 JSON）
        stdout = result.stdout.strip()
        if stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                # 如果整个 stdout 不是 JSON，尝试从最后一行找
                lines = stdout.splitlines()
                for line in reversed(lines):
                    line = line.strip()
                    if line and line.startswith(("{", "[")):
                        return json.loads(line)
        return {}
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] lark-cli failed: {e.stderr}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"   [ERROR] Failed to parse lark-cli output: {e}", file=sys.stderr)
        return {}


def fetch_wiki_nodes_recursive(
    space_id: str,
    parent_node_token: str = "",
    _visited: set[str] | None = None,
    _depth: int = 0,
) -> list[dict]:
    """递归获取 Wiki 空间下所有节点（含 folder 展开）

    Args:
        space_id: Wiki 空间 ID
        parent_node_token: 父节点 token（空字符串表示根节点）
        _visited: 内部使用，防止循环引用和重复扫描
        _depth: 内部使用，当前递归深度
    """
    if _visited is None:
        _visited = set()

    # 防止循环引用
    if parent_node_token in _visited:
        return []
    if parent_node_token:
        _visited.add(parent_node_token)

    all_nodes: list[dict] = []
    page_token = ""
    page_count = 0
    indent = "  " * _depth

    if _depth == 0:
        print(f"  Scanning root nodes...")
    else:
        print(f"{indent}  Scanning children of {parent_node_token[:12]}...", end="", flush=True)

    while True:
        params: dict[str, str] = {"space_id": space_id}
        if parent_node_token:
            params["parent_node_token"] = parent_node_token
        if page_token:
            params["page_token"] = page_token

        result = run_lark_cli([
            "wiki", "nodes", "list",
            "--params", json.dumps(params, ensure_ascii=False),
            "--format", "json"
        ])

        items = result.get("data", {}).get("items", [])
        if not items:
            items = result.get("items", [])

        all_nodes.extend(items)
        page_count += 1

        has_more = result.get("data", {}).get("has_more", False)
        if not has_more:
            has_more = result.get("has_more", False)
        page_token = result.get("data", {}).get("page_token", "")
        if not page_token:
            page_token = result.get("page_token", "")

        if not has_more or not page_token:
            break

    if _depth > 0:
        print(f" {len(all_nodes)} nodes")

    # 递归展开有子节点的节点（飞书 Wiki 中 folder 也是 docx，用 has_child 判断）
    for node in all_nodes:
        if node.get("has_child", False):
            child_token = node.get("node_token", "")
            if child_token and child_token not in _visited:
                children = fetch_wiki_nodes_recursive(
                    space_id, child_token, _visited=_visited, _depth=_depth + 1
                )
                all_nodes.extend(children)

    return all_nodes


def build_node_path_map(nodes: list[dict]) -> dict[str, str]:
    """构建 node_token -> 完整路径（title1/title2/...）的映射"""
    parent_map = {}
    title_map = {}
    for node in nodes:
        token = node.get("node_token", "")
        title_map[token] = node.get("title", "Untitled")
        parent_map[token] = node.get("parent_node_token", "")

    path_map = {}
    for node in nodes:
        token = node.get("node_token", "")
        parts = []
        current = token
        visited = set()
        while current and current not in visited:
            visited.add(current)
            parts.append(title_map.get(current, "Unknown"))
            current = parent_map.get(current, "")
        parts.reverse()
        path_map[token] = "/".join(parts) if parts else ""

    return path_map


def load_sources_yaml() -> dict:
    """读取 sources.yaml"""
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    if not SOURCES_YAML.exists():
        return {"wiki": {"space": {"space_id": ""}, "scope_rules": [], "nodes": []}, "base": []}

    return yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8")) or {}


def save_sources_yaml(data: dict):
    """写入 sources.yaml，保留头部注释"""
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML not installed.", file=sys.stderr)
        sys.exit(1)

    # 备份
    if SOURCES_YAML.exists():
        backup = SOURCES_YAML.with_suffix(".yaml.bak")
        shutil.copy2(SOURCES_YAML, backup)
        print(f"   Backup: {backup.name}")

    original_content = SOURCES_YAML.read_text(encoding="utf-8") if SOURCES_YAML.exists() else ""
    lines = original_content.splitlines()

    # 提取头部注释（文件开头的所有注释和空行）
    header_lines = []
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            body_start = i
            break
        header_lines.append(line)

    # dump 新数据
    new_body = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)

    # 合并头部注释 + 新数据
    new_content = "\n".join(header_lines) + "\n" + new_body if header_lines else new_body
    SOURCES_YAML.write_text(new_content, encoding="utf-8")


def infer_scope(node_path: str, scope_rules: list[dict]) -> tuple[str, str | None]:
    """根据路径推断 scope 和 project_id

    匹配逻辑（按优先级）：
    1. 路径中某一段精确匹配 pattern（去 * 后）
    2. 路径中某一段以 pattern 开头（支持如"虚拟IP孵化"匹配"虚拟IP孵化与运营"）
    """
    path_parts = node_path.split("/")
    for rule in scope_rules:
        pattern = rule.get("path", "").rstrip("/*")
        if not pattern:
            continue
        # 精确匹配
        if pattern in path_parts:
            return rule.get("scope", "pending"), rule.get("project_id")
        # 前缀匹配（pattern 长度 >= 3 才启用，避免过短前缀误匹配）
        if len(pattern) >= 3:
            for part in path_parts:
                if part.startswith(pattern):
                    return rule.get("scope", "pending"), rule.get("project_id")
    return "pending", None


def discover(space_id: str, dry_run: bool = False, save_report: bool = False) -> dict:
    """执行发现流程"""
    print(f"\n🔍 Discovering Wiki space: {space_id}")

    # 1. 加载现有配置
    config = load_sources_yaml()
    existing_nodes = config.get("wiki", {}).get("nodes", [])
    scope_rules = config.get("wiki", {}).get("scope_rules", [])

    existing_by_token: dict[str, dict] = {}
    for node in existing_nodes:
        token = node.get("node_token", "")
        if token:
            existing_by_token[token] = node

    # 2. 递归扫描飞书 Wiki
    print("  Scanning Feishu Wiki nodes...")
    remote_nodes = fetch_wiki_nodes_recursive(space_id)
    print(f"  Found {len(remote_nodes)} total nodes")

    # 3. 构建路径映射
    path_map = build_node_path_map(remote_nodes)

    # 4. 筛选 docx 节点
    remote_docx: dict[str, dict] = {}
    for node in remote_nodes:
        node_type = node.get("obj_type") or node.get("type", "")
        if node_type == "docx":
            token = node.get("node_token", "")
            if token:
                remote_docx[token] = node

    print(f"  Filtered {len(remote_docx)} docx nodes")

    # 5. 对比分析
    added: list[dict] = []
    updated: list[dict] = []
    missing: list[dict] = []
    unchanged_count = 0

    remote_tokens = set(remote_docx.keys())
    existing_tokens = set(existing_by_token.keys())

    # 新增节点
    for token in sorted(remote_tokens - existing_tokens):
        node = remote_docx[token]
        path = path_map.get(token, "")
        scope, project_id = infer_scope(path, scope_rules)

        new_entry = {
            "node_token": token,
            "obj_token": node.get("obj_token", ""),
            "title": node.get("title", "Untitled"),
            "scope": scope,
            "type": "docx",
            "lark_url": f"https://ncnkdep1f4r7.feishu.cn/wiki/{token}",
        }
        if project_id:
            new_entry["project_id"] = project_id

        added.append({
            "entry": new_entry,
            "path": path,
            "note": "scope pending" if scope == "pending" else None,
        })

    # 变更节点
    for token in sorted(remote_tokens & existing_tokens):
        remote = remote_docx[token]
        existing = existing_by_token[token]
        changes: dict[str, dict] = {}

        if remote.get("title") != existing.get("title"):
            changes["title"] = {"old": existing.get("title"), "new": remote.get("title")}

        remote_obj = remote.get("obj_token", "")
        existing_obj = existing.get("obj_token", "")
        if remote_obj and remote_obj != existing_obj:
            changes["obj_token"] = {"old": existing_obj, "new": remote_obj}

        # scope 漂移检测（已有明确 scope 的节点不降级为 pending）
        path = path_map.get(token, "")
        new_scope, new_project_id = infer_scope(path, scope_rules)
        existing_scope = existing.get("scope", "pending")
        if new_scope != existing_scope and not (new_scope == "pending" and existing_scope != "pending"):
            changes["scope"] = {"old": existing_scope, "new": new_scope}
        existing_pid = existing.get("project_id")
        if new_project_id != existing_pid and not (new_project_id is None and existing_pid is not None):
            changes["project_id"] = {"old": existing_pid, "new": new_project_id}

        if changes:
            updated.append({"token": token, "changes": changes, "path": path})
        else:
            unchanged_count += 1

    # 缺失节点（yaml 有，飞书无）— 只报告 docx，不报告 bitable
    for token in sorted(existing_tokens - remote_tokens):
        existing = existing_by_token[token]
        if existing.get("type") == "docx":
            missing.append({
                "token": token,
                "title": existing.get("title"),
                "path": "",
            })

    # 6. 输出报告
    print(f"\n{'='*50}")
    print("Discover Report")
    print(f"{'='*50}")
    print(f"  Added:     {len(added)}")
    print(f"  Updated:   {len(updated)}")
    print(f"  Missing:   {len(missing)} (report only)")
    print(f"  Unchanged: {unchanged_count}")

    if added:
        print(f"\n  --- Added ---")
        for item in added:
            entry = item["entry"]
            flag = " [PENDING scope]" if entry.get("scope") == "pending" else ""
            print(f"    + {entry['title']}{flag}")
            print(f"      path: {item['path']}")
            print(f"      node_token: {entry['node_token']}")

    if updated:
        print(f"\n  --- Updated ---")
        for item in updated:
            print(f"    ~ {item['changes']}")

    if missing:
        print(f"\n  --- Missing (not removed from yaml) ---")
        for item in missing:
            print(f"    ? {item['title']} ({item['token']})")

    # 7. 更新 yaml
    if not dry_run:
        # 应用更新到数据结构
        node_map = {n.get("node_token", ""): n for n in config["wiki"]["nodes"]}

        for item in added:
            entry = item["entry"]
            config["wiki"]["nodes"].append(entry)

        for item in updated:
            token = item["token"]
            if token in node_map:
                for key, change in item["changes"].items():
                    node_map[token][key] = change["new"]

        save_sources_yaml(config)
        print(f"\n   Updated: {SOURCES_YAML}")
    else:
        print(f"\n   [DRY-RUN] No changes written")

    # 8. 生成报告文件
    report = {
        "timestamp": datetime.now().isoformat(),
        "space_id": space_id,
        "dry_run": dry_run,
        "summary": {
            "total_remote": len(remote_nodes),
            "total_remote_docx": len(remote_docx),
            "total_existing_docx": len([n for n in existing_nodes if n.get("type") == "docx"]),
            "added": len(added),
            "updated": len(updated),
            "missing": len(missing),
            "unchanged": unchanged_count,
        },
        "added": added,
        "updated": updated,
        "missing": missing,
    }

    if save_report:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        DISCOVER_REPORT.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"   Report: {DISCOVER_REPORT}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Discover Feishu Wiki nodes and update sources.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--report", action="store_true", help="Save report to state/discover_report.json")
    args = parser.parse_args()

    config = load_sources_yaml()
    space_id = config.get("wiki", {}).get("space", {}).get("space_id", "")

    if not space_id:
        print("Error: space_id not found in sources.yaml", file=sys.stderr)
        sys.exit(1)

    discover(space_id, dry_run=args.dry_run, save_report=args.report)


if __name__ == "__main__":
    main()
