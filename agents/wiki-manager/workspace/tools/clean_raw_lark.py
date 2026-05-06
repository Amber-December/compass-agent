#!/usr/bin/env python3
"""
Clean Raw Lark — 存量 raw_lark 文档批量清洗

对现有 raw_lark/wiki/ 下的所有 .md 文件执行一次性清洗：
1. <lark-table> XML → markdown pipe table
2. 移除文末冗余的"飞书 Wiki 在线地址"脚注
3. 重建 frontmatter：保留来源元数据，去除 wiki 运行时状态字段，添加 doc_type 和 content_hash

Usage:
    python tools/clean_raw_lark.py --dry-run   # 预览变更
    python tools/clean_raw_lark.py             # 执行清洗
"""

import sys
import re
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# tools/ -> agents/wiki-manager/ -> agents/ -> workspace/
def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

REPO_ROOT = _find_repo_root()
AGENT_WORKSPACE = REPO_ROOT / "agents" / "wiki-manager" / "workspace"
RAW_LARK_WIKI_DIR = AGENT_WORKSPACE / "raw_lark" / "wiki"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def extract_frontmatter(content: str) -> tuple[dict, str]:
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


def convert_lark_tables(content: str) -> str:
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


def detect_doc_type(title: str, content: str, rel_path: str) -> str:
    title_lower = title.lower()
    path_lower = rel_path.lower()
    content_preview = content[:3000].lower()

    if '周报归档' in path_lower:
        if '部门' in title or 'mcn事业部' in title_lower:
            return 'dept-weekly'
        return 'project-weekly'
    if '会议纪要' in path_lower:
        return 'meeting'
    if '项目文档' in path_lower:
        return 'project-doc'

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


def remove_feishu_footer(content: str) -> str:
    footer_pattern = r'\n---\n\n\*\*飞书 Wiki 在线地址\*\*：.*?\n?$'
    cleaned = re.sub(footer_pattern, '', content, flags=re.DOTALL)
    return cleaned


def clean_file(filepath: Path, dry_run: bool = False) -> dict:
    content = filepath.read_text(encoding='utf-8')
    old_fm, body = extract_frontmatter(content)

    if not old_fm:
        print(f"   ⚠️  No frontmatter, skipping: {filepath.name}")
        return {"status": "skipped", "reason": "no_frontmatter"}

    # 1. 转换表格
    new_body = convert_lark_tables(body)
    table_converted = new_body != body

    # 2. 移除脚注
    new_body = remove_feishu_footer(new_body)

    # 3. 判定 doc_type
    rel_path = str(filepath.relative_to(RAW_LARK_WIKI_DIR))
    title = old_fm.get('title', filepath.stem)
    doc_type = detect_doc_type(title, new_body, rel_path)

    # 4. 重建干净 frontmatter
    body_hash = sha256_text(new_body)
    new_fm = {
        "title": title,
        "doc_type": doc_type,
        "scope": old_fm.get('scope', 'public'),
        "lark_url": old_fm.get('lark_url', ''),
        "lark_node_id": old_fm.get('lark_node_id', ''),
        "content_hash": body_hash,
        "fetched_at": old_fm.get('fetched_at', datetime.now().isoformat()),
        "status": old_fm.get('status', 'active'),
    }
    if old_fm.get('project_id'):
        new_fm["project_id"] = old_fm["project_id"]

    new_content = build_frontmatter(new_fm) + new_body

    # 5. 判断是否真的有变化
    if new_content.strip() == content.strip():
        print(f"   ✅ No effective change: {filepath.name}")
        return {"status": "unchanged", "path": str(filepath)}

    if dry_run:
        print(f"   🧪 Would clean: {filepath.name} (doc_type={doc_type})")
        if table_converted:
            print(f"      📊 Lark tables → markdown")
        return {"status": "dry_run", "path": str(filepath), "doc_type": doc_type}

    filepath.write_text(new_content, encoding='utf-8')
    print(f"   ✏️  Cleaned: {filepath.name} (doc_type={doc_type})")
    if table_converted:
        print(f"      📊 Lark tables converted to markdown")
    return {"status": "cleaned", "path": str(filepath), "doc_type": doc_type}


def main():
    parser = argparse.ArgumentParser(description="Clean existing raw_lark files")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    md_files = list(RAW_LARK_WIKI_DIR.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files in {RAW_LARK_WIKI_DIR}")
    print(f"Mode: {'dry-run' if args.dry_run else 'write'}\n")

    stats = {"cleaned": 0, "unchanged": 0, "skipped": 0, "dry_run": 0}
    for filepath in sorted(md_files):
        result = clean_file(filepath, dry_run=args.dry_run)
        stats[result["status"]] = stats.get(result["status"], 0) + 1

    print(f"\n{'='*50}")
    print("Summary")
    print(f"{'='*50}")
    for k, v in stats.items():
        if v > 0:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
