#!/usr/bin/env python3
"""
base_sync.py - wiki-manager 的 Base 数据同步工具

从飞书多维表格拉取数据并保存到本地缓存。
"""

import os
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

REPO_ROOT = _find_repo_root()
DATA_DIR = REPO_ROOT / "workspace" / "knowledge" / "data"

def run_lark_cli(cmd_args):
    """运行 lark-cli 命令"""
    result = subprocess.run(
        ["lark-cli"] + cmd_args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    if result.returncode != 0:
        print(f"❌ 命令失败: {result.stderr}")
        return None
    return json.loads(result.stdout)

def sync_base_data(base_token, table_name_or_id, output_dir):
    """同步 Base 表格数据（实时从飞书拉取）"""
    print(f"📊 同步 Base: {base_token}/{table_name_or_id}")
    
    # 使用司南 profile 拉取
    records = run_lark_cli([
        "base", "+record-list",
        "--base-token", base_token,
        "--table-id", table_name_or_id,
        "--as", "user",
        "--profile", "compass",
        "--limit", "500"
    ])
    
    if not records or not records.get("ok"):
        print(f"⚠️ 无法拉取记录，尝试从快照读取...")
        return sync_from_snapshot(output_dir)
    
    # 保存到本地
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[^\w]', '_', table_name_or_id)
    output_file = output_dir / f"{safe_name}_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    items = records.get('data', {}).get('data', [])
    print(f"  ✓ 保存到: {output_file}")
    print(f"  ✓ 记录数: {len(items)}")
    
    return records

def sync_from_snapshot(snapshot_dir):
    """从已有快照读取数据（权限不足时的降级方案）"""
    snapshot_dir = Path(snapshot_dir)
    
    if not snapshot_dir.exists():
        print(f"❌ 快照目录不存在: {snapshot_dir}")
        return None
    
    print(f"📂 读取本地快照: {snapshot_dir}")
    
    data = {}
    for json_file in snapshot_dir.glob("*.json"):
        if "_meta" in json_file.name:
            continue
        
        table_name = json_file.stem
        with open(json_file, 'r', encoding='utf-8') as f:
            data[table_name] = json.load(f)
        
        print(f"  ✓ {table_name}: {len(data[table_name])} 条记录")
    
    return data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python base_sync.py sync <base_token> <table_name> [output_dir]")
        print("  python base_sync.py snapshot <snapshot_dir>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "sync":
        base_token = sys.argv[2]
        table_name = sys.argv[3]
        output_dir = sys.argv[4] if len(sys.argv) > 4 else str(DATA_DIR / base_token)
        sync_base_data(base_token, table_name, output_dir)
    
    elif cmd == "snapshot":
        snapshot_dir = sys.argv[2]
        sync_from_snapshot(snapshot_dir)
    
    else:
        print(f"未知命令: {cmd}")
