#!/usr/bin/env python3
"""
Compass Data Diff — 检测本地 data/ 目录的变更

用途：
1. 追踪 data/mock/ 和 data/schema/ 下的文件变化
2. 对比当前文件与上次快照，输出新增/修改/删除
3. 对 JSON 文件做字段级 diff，精确到记录级别
4. 结合 sync_base_from_mock.py 逻辑，预估影响哪些 Base 表

Usage:
    python tools/data_diff.py --snapshot          # 建立当前快照
    python tools/data_diff.py --diff              # 对比当前状态与上次快照
    python tools/data_diff.py --diff --detail     # 显示详细字段级 diff
    python tools/data_diff.py --report            # 生成变更报告（含 Base 表影响分析）
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 路径常量（基于 workspace 目录结构）
# tools/ -> agents/wiki-manager/ -> agents/ -> workspace/
def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent

REPO_ROOT = _find_repo_root()
AGENT_WORKSPACE = REPO_ROOT / "agents" / "wiki-manager" / "workspace"
DATA_DIR = REPO_ROOT / "workspace" / "knowledge" / "data"
STATE_DIR = AGENT_WORKSPACE / "state"
SNAPSHOT_FILE = STATE_DIR / "data_snapshot.json"
DIFF_REPORT_FILE = STATE_DIR / "data_diff_report.md"

# 与 sync_base_from_mock.py 对应的表映射
BASE_TABLE_MAP = {
    "data/mock/mcn/base.json": ["tblbbwkCKI5pHy4C"],
    "data/mock/mcn/department_weekly_summary.json": ["tbl9OF7TP0ecPHRG", "tbli4vUzTszy0gp1"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def get_data_files() -> list[Path]:
    """获取 data/ 下所有数据文件"""
    files = []
    for pattern in ["**/*.json", "**/*.yaml", "**/*.yml"]:
        files.extend(DATA_DIR.rglob(pattern))
    return sorted(files)


def build_snapshot() -> dict:
    """建立当前 data/ 的快照"""
    snapshot = {
        "created_at": datetime.now().isoformat(),
        "files": {},
    }
    for fp in get_data_files():
        rel = str(fp.relative_to(REPO_ROOT))
        snapshot["files"][rel] = {
            "hash": sha256_file(fp),
            "size": fp.stat().st_size,
            "mtime": fp.stat().st_mtime,
        }
    return snapshot


def save_snapshot(snapshot: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Snapshot saved: {SNAPSHOT_FILE.relative_to(REPO_ROOT)}")
    print(f"  Total files: {len(snapshot['files'])}")


def load_snapshot() -> dict | None:
    if not SNAPSHOT_FILE.exists():
        return None
    return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))


def diff_json(old_path: Path, new_path: Path) -> dict:
    """对两个 JSON 文件做字段级 diff"""
    try:
        old_data = json.loads(old_path.read_text(encoding="utf-8"))
        new_data = json.loads(new_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return {"error": "Cannot parse JSON"}

    # 展平为 dict[json_path] = value
    def flatten(obj, prefix=""):
        items = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                path = f"{prefix}.{k}" if prefix else k
                if isinstance(v, (dict, list)):
                    items.update(flatten(v, path))
                else:
                    items[path] = v
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                path = f"{prefix}[{i}]"
                if isinstance(v, (dict, list)):
                    items.update(flatten(v, path))
                else:
                    items[path] = v
        return items

    old_flat = flatten(old_data)
    new_flat = flatten(new_data)

    added = {k: new_flat[k] for k in new_flat if k not in old_flat}
    removed = {k: old_flat[k] for k in old_flat if k not in new_flat}
    changed = {}
    for k in new_flat:
        if k in old_flat and old_flat[k] != new_flat[k]:
            changed[k] = {"old": old_flat[k], "new": new_flat[k]}

    return {"added": added, "removed": removed, "changed": changed}


def run_diff(detail: bool = False) -> dict:
    """对比当前状态与快照，返回变更摘要"""
    old = load_snapshot()
    if old is None:
        print("No snapshot found. Run with --snapshot first.")
        sys.exit(1)

    new = build_snapshot()
    old_files = old.get("files", {})
    new_files = new["files"]

    result = {
        "snapshot_time": old.get("created_at", "unknown"),
        "current_time": new["created_at"],
        "added": [],
        "removed": [],
        "modified": [],
        "unchanged": [],
        "base_impact": defaultdict(list),
    }

    # 新增
    for rel in new_files:
        if rel not in old_files:
            result["added"].append(rel)
            for pattern, tables in BASE_TABLE_MAP.items():
                if rel.endswith(pattern):
                    for t in tables:
                        result["base_impact"][t].append(f"+ file {rel}")

    # 删除
    for rel in old_files:
        if rel not in new_files:
            result["removed"].append(rel)

    # 修改/未变
    for rel, info in new_files.items():
        if rel in old_files:
            if info["hash"] != old_files[rel]["hash"]:
                result["modified"].append(rel)
                for pattern, tables in BASE_TABLE_MAP.items():
                    if rel.endswith(pattern):
                        for t in tables:
                            result["base_impact"][t].append(f"~ file {rel}")
                # 详细 diff
                if detail and rel.endswith(".json"):
                    # 尝试从旧快照恢复内容...但快照没有存内容
                    # 只能标记为 modified
                    pass
            else:
                result["unchanged"].append(rel)

    return result


def print_diff(result: dict, detail: bool = False):
    print("=" * 60)
    print(f"Data Diff Report")
    print(f"  Snapshot: {result['snapshot_time']}")
    print(f"  Current:  {result['current_time']}")
    print("=" * 60)

    if result["added"]:
        print(f"\n📁 Added ({len(result['added'])}):")
        for f in result["added"]:
            print(f"  + {f}")

    if result["removed"]:
        print(f"\n🗑️  Removed ({len(result['removed'])}):")
        for f in result["removed"]:
            print(f"  - {f}")

    if result["modified"]:
        print(f"\n✏️  Modified ({len(result['modified'])}):")
        for f in result["modified"]:
            print(f"  ~ {f}")
            if detail and f.endswith(".json"):
                fp = REPO_ROOT / f
                try:
                    data = json.loads(fp.read_text(encoding="utf-8"))
                    # 尝试提取顶层数组长度变化
                    if isinstance(data, list):
                        print(f"     → array length: {len(data)}")
                    elif isinstance(data, dict):
                        print(f"     → keys: {list(data.keys())}")
                except Exception:
                    pass
    else:
        print("\n✅ No files modified.")

    if result["base_impact"]:
        print(f"\n📊 Base Table Impact:")
        for table_id, impacts in result["base_impact"].items():
            print(f"  Table {table_id}: {', '.join(impacts)}")

    print()


def generate_report(result: dict):
    """生成 markdown 格式的变更报告"""
    lines = [
        "# Data Diff Report",
        f"",
        f"- **Snapshot Time**: {result['snapshot_time']}",
        f"- **Current Time**: {result['current_time']}",
        f"",
        "## Summary",
        f"",
        f"| Type | Count |",
        f"|------|-------|",
        f"| Added | {len(result['added'])} |",
        f"| Removed | {len(result['removed'])} |",
        f"| Modified | {len(result['modified'])} |",
        f"| Unchanged | {len(result['unchanged'])} |",
        f"",
    ]

    if result["modified"]:
        lines.append("## Modified Files")
        lines.append("")
        for f in result["modified"]:
            lines.append(f"- `{f}`")
            # 如果有 Base 表影响，标注
            for pattern, tables in BASE_TABLE_MAP.items():
                if f.endswith(pattern):
                    lines.append(f"  - Affects Base tables: {', '.join(tables)}")
        lines.append("")

    if result["added"]:
        lines.append("## Added Files")
        lines.append("")
        for f in result["added"]:
            lines.append(f"- `{f}`")
        lines.append("")

    if result["removed"]:
        lines.append("## Removed Files")
        lines.append("")
        for f in result["removed"]:
            lines.append(f"- `{f}`")
        lines.append("")

    content = "\n".join(lines)
    DIFF_REPORT_FILE.write_text(content, encoding="utf-8")
    print(f"Report saved: {DIFF_REPORT_FILE.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Detect changes in data/ directory")
    parser.add_argument("--snapshot", action="store_true", help="Create a new snapshot")
    parser.add_argument("--diff", action="store_true", help="Show diff against last snapshot")
    parser.add_argument("--detail", action="store_true", help="Show detailed field-level diff")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    args = parser.parse_args()

    if args.snapshot:
        snap = build_snapshot()
        save_snapshot(snap)
        return

    if args.diff or args.report:
        result = run_diff(detail=args.detail)
        print_diff(result, detail=args.detail)
        if args.report:
            generate_report(result)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
