#!/usr/bin/env python3
"""
Compass Scheduler — 统一调度器，编排三条流水线

流水线：
1. Base 数据同步（base_sync.py）
2. Wiki 文档同步（wiki_sync.py）
3. 知识编译（wiki_ingest.py，可选自动触发）
4. 图谱构建（build_graph.py，可选自动触发）

Usage:
    python tools/scheduler.py --full-sync           # 全量同步 + 自动 ingest + 建图
    python tools/scheduler.py --base-only           # 仅同步 Base
    python tools/scheduler.py --wiki-only --ingest  # 仅同步 Wiki 并自动 ingest
    python tools/scheduler.py --dry-run             # 模拟运行，不写入
    python tools/scheduler.py --report              # 打印当前状态报告
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


# 路径常量（基于项目根目录）
def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent

REPO_ROOT = _find_repo_root()
AGENT_WORKSPACE = REPO_ROOT / "agents" / "wiki-manager" / "workspace"
TOOLS_DIR = AGENT_WORKSPACE / "tools"
STATE_DIR = AGENT_WORKSPACE / "state"
SYNC_STATE_FILE = STATE_DIR / "sync_state.json"
LOCK_FILE = STATE_DIR / "scheduler.lock"
LOG_FILE = STATE_DIR / "scheduler.log"
WIKI_LOG_FILE = REPO_ROOT / "workspace" / "knowledge" / "wiki" / "log.md"


def log(msg: str):
    ts = datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    if LOG_FILE:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def acquire_lock(timeout_seconds: int = 1800) -> bool:
    """获取调度锁，防止并发执行。如果锁已存在但超时，则强制获取。"""
    if LOCK_FILE.exists():
        try:
            lock_time = datetime.fromisoformat(LOCK_FILE.read_text().strip())
            if (datetime.now() - lock_time).total_seconds() < timeout_seconds:
                return False
        except Exception:
            pass
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(datetime.now().isoformat(), encoding="utf-8")
    return True


def release_lock():
    LOCK_FILE.unlink(missing_ok=True)


def append_wiki_log(entry: str):
    """追加一行到 workspace/knowledge/wiki/log.md"""
    WIKI_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if WIKI_LOG_FILE.exists():
        content = WIKI_LOG_FILE.read_text(encoding="utf-8")
    else:
        content = "# Compass 知识库日志\n\n"
    content = content.rstrip() + "\n\n" + entry.strip() + "\n"
    WIKI_LOG_FILE.write_text(content, encoding="utf-8")


def run_script(script_name: str, *args) -> tuple[int, str, str]:
    """运行子脚本，返回 (returncode, stdout, stderr)"""
    cmd = [sys.executable, str(TOOLS_DIR / script_name)] + list(args)
    log(f"Run: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(AGENT_WORKSPACE))
    if result.returncode != 0:
        log(f"  ⚠️  {script_name} exited with code {result.returncode}")
        if result.stderr.strip():
            for line in result.stderr.strip().split("\n")[:5]:
                log(f"    stderr: {line}")
    return result.returncode, result.stdout, result.stderr


def load_sync_state() -> dict:
    if SYNC_STATE_FILE.exists():
        state = json.loads(SYNC_STATE_FILE.read_text(encoding="utf-8"))
        # Ensure pipelines key exists
        if "pipelines" not in state:
            state["pipelines"] = {"base": {}, "wiki": {}, "ingest": {}, "graph": {}}
        return state
    return {
        "last_scheduler_run": None,
        "pipelines": {"base": {}, "wiki": {}, "ingest": {}, "graph": {}}
    }


def save_sync_state(state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_wiki_sync_summary(stdout: str) -> dict:
    """从 wiki_sync.py 的输出解析摘要"""
    summary = {"synced": 0, "unchanged": 0, "skipped": 0, "errors": 0, "archived": 0, "synced_files": [], "archived_files": []}
    for line in stdout.split("\n"):
        line = line.strip()
        if line.startswith("Synced  :"):
            summary["synced"] = int(line.split(":")[1].strip())
        elif line.startswith("Unchanged:"):
            summary["unchanged"] = int(line.split(":")[1].strip())
        elif line.startswith("Skipped :"):
            summary["skipped"] = int(line.split(":")[1].strip())
        elif line.startswith("Archived:"):
            summary["archived"] = int(line.split(":")[1].strip())
        elif line.startswith("Errors  :"):
            summary["errors"] = int(line.split(":")[1].strip())
        elif line.startswith("__SYNC_REPORT__="):
            try:
                json_str = line.split("__SYNC_REPORT__=", 1)[1].rsplit("__", 1)[0]
                report = json.loads(json_str)
                summary["synced_files"] = report.get("synced_files", [])
                summary["archived_files"] = report.get("archived_files", [])
            except Exception:
                pass
    return summary


def parse_base_sync_summary(stdout: str) -> dict:
    """从 base_sync.py 的输出解析摘要"""
    summary = {"success": 0, "errors": 0, "total_records": 0}
    for line in stdout.split("\n"):
        line = line.strip()
        if line.startswith("Success:"):
            summary["success"] = int(line.split(":")[1].strip())
        elif line.startswith("Errors:"):
            summary["errors"] = int(line.split(":")[1].strip())
        elif line.startswith("Total records:"):
            summary["total_records"] = int(line.split(":")[1].strip())
    return summary


def run_base_sync(dry_run: bool = False) -> dict:
    log("=" * 60)
    log("Pipeline: Base Sync")
    log("=" * 60)
    args = ["--all"]
    if dry_run:
        args.append("--dry-run")
    code, stdout, stderr = run_script("base_sync.py", *args)
    summary = parse_base_sync_summary(stdout)
    summary["ok"] = code == 0
    log(f"Base Sync: success={summary['success']}, errors={summary['errors']}, records={summary['total_records']}")
    return summary


def run_wiki_sync(dry_run: bool = False, auto_ingest: bool = False) -> dict:
    log("=" * 60)
    log("Pipeline: Wiki Sync")
    log("=" * 60)
    args = ["--all"]
    if dry_run:
        args.append("--dry-run")
    if auto_ingest:
        args.append("--ingest")
    code, stdout, stderr = run_script("wiki_sync.py", *args)
    summary = parse_wiki_sync_summary(stdout)
    summary["ok"] = code == 0
    log(f"Wiki Sync: synced={summary['synced']}, unchanged={summary['unchanged']}, skipped={summary['skipped']}, errors={summary['errors']}")
    return summary


def run_wiki_ingest(file_paths: list[str] | None = None, scope_filter: str | None = None, dry_run: bool = False) -> dict:
    log("=" * 60)
    log("Pipeline: Wiki Ingest")
    log("=" * 60)
    raw_wiki_dir = AGENT_WORKSPACE / "raw_lark" / "wiki"
    if not raw_wiki_dir.exists():
        log(f"Wiki Ingest: raw_lark/wiki/ not found, skipping")
        return {"ok": True, "ingested": 0}

    ingest_script = AGENT_WORKSPACE / "tools" / "wiki_ingest.py"

    if file_paths:
        # Incremental ingest: only process changed files
        log(f"Wiki Ingest: incremental mode, {len(file_paths)} files")
        ingested = 0
        for fpath in file_paths:
            full_path = AGENT_WORKSPACE / fpath
            if not full_path.exists():
                log(f"  ⚠️  File not found, skipping: {fpath}")
                continue
            if dry_run:
                log(f"  🧪 Dry run: would ingest {fpath}")
                continue
            code, stdout, stderr = run_script("wiki_ingest.py", str(full_path))
            if code == 0:
                ingested += 1
        log(f"Wiki Ingest: incremental completed ({ingested}/{len(file_paths)} ingested)")
        return {"ok": True, "ingested": ingested}
    else:
        # Full batch ingest (fallback)
        log(f"Wiki Ingest: full batch mode")
        args = ["--batch", str(raw_wiki_dir)]
        if scope_filter:
            args.extend(["--scope", scope_filter])
        if dry_run:
            args.append("--dry-run")

        code, stdout, stderr = run_script("wiki_ingest.py", *args)
        log(f"Wiki Ingest: batch completed (exit code {code})")
        return {"ok": code == 0, "ingested": -1}


def run_graph_build(dry_run: bool = False) -> dict:
    log("=" * 60)
    log("Pipeline: Graph Build")
    log("=" * 60)
    args = []
    if dry_run:
        log("Graph Build: dry-run mode, skipping")
        return {"ok": True}
    code, stdout, stderr = run_script("build_graph.py", *args)
    log(f"Graph Build: completed (exit code {code})")
    return {"ok": code == 0}


def print_report(state: dict):
    log("=" * 60)
    log("Compass Scheduler Report")
    log("=" * 60)
    pipelines = state.get("pipelines", {})
    for name, data in pipelines.items():
        status = "✅" if data.get("ok") else "❌"
        ts = data.get("at", "never")
        log(f"  {status} {name:12s} @ {ts}")
    log("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Compass Scheduler — orchestrate all pipelines")
    parser.add_argument("--full-sync", action="store_true", help="Run base + wiki + ingest + graph")
    parser.add_argument("--base-only", action="store_true", help="Only sync Base data")
    parser.add_argument("--wiki-only", action="store_true", help="Only sync Wiki docs")
    parser.add_argument("--ingest", action="store_true", help="Auto-trigger wiki ingest after sync")
    parser.add_argument("--graph", action="store_true", help="Auto-trigger graph build after ingest")
    parser.add_argument("--dry-run", action="store_true", help="Simulation mode")
    parser.add_argument("--report", action="store_true", help="Print status report")
    args = parser.parse_args()

    if args.report:
        state = load_sync_state()
        print_report(state)
        return

    if not args.full_sync and not args.base_only and not args.wiki_only:
        parser.print_help()
        print("\nHint: Use --full-sync for complete refresh, or --base-only / --wiki-only for partial.")
        sys.exit(1)

    # Acquire lock to prevent concurrent execution
    if not acquire_lock():
        log("Sync already in progress (lock held). Exiting.")
        sys.exit(0)

    state = load_sync_state()
    now = datetime.now().isoformat()
    synced_files = []
    archived_files = []

    try:
        # Base Sync
        if args.full_sync or args.base_only:
            base_result = run_base_sync(dry_run=args.dry_run)
            state["pipelines"]["base"] = {**base_result, "at": now}

        # Wiki Sync
        if args.full_sync or args.wiki_only:
            wiki_result = run_wiki_sync(dry_run=args.dry_run, auto_ingest=False)
            state["pipelines"]["wiki"] = {**wiki_result, "at": now}
            synced_files = wiki_result.get("synced_files", [])
            archived_files = wiki_result.get("archived_files", [])

        # Incremental Ingest: only process changed files
        if (args.ingest or args.full_sync) and not args.dry_run:
            if synced_files:
                ingest_result = run_wiki_ingest(file_paths=synced_files, dry_run=args.dry_run)
            else:
                log("Wiki Ingest: no changed files, skipping")
                ingest_result = {"ok": True, "ingested": 0}
            state["pipelines"]["ingest"] = {**ingest_result, "at": now}

        # Graph Build
        if (args.graph or args.full_sync) and not args.dry_run:
            graph_result = run_graph_build(dry_run=args.dry_run)
            state["pipelines"]["graph"] = {**graph_result, "at": now}

        # Write workspace/knowledge/wiki/log.md
        if not args.dry_run:
            base_summary = state.get("pipelines", {}).get("base", {})
            wiki_summary = state.get("pipelines", {}).get("wiki", {})
            base_ok = "✅" if base_summary.get("ok") else "❌"
            wiki_ok = "✅" if wiki_summary.get("ok") else "❌"
            log_entry = (
                f"## [{now[:16].replace('T', ' ')}] sync | "
                f"新增 {wiki_summary.get('synced', 0)} 修改 {wiki_summary.get('unchanged', 0)} 归档 {len(archived_files)}\n"
                f"- Base: {base_ok} {base_summary.get('success', 0)} 张表, {base_summary.get('total_records', 0)} 条记录\n"
                f"- Wiki: {wiki_ok} 新增 {wiki_summary.get('synced', 0)}, 修改 {wiki_summary.get('unchanged', 0)}, "
                f"跳过 {wiki_summary.get('skipped', 0)}, 归档 {len(archived_files)}, 错误 {wiki_summary.get('errors', 0)}"
            )
            append_wiki_log(log_entry)
            log("Wiki log updated")

        state["last_scheduler_run"] = now
        save_sync_state(state)

        print_report(state)
    finally:
        release_lock()


if __name__ == "__main__":
    main()
