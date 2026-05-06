#!/usr/bin/env python3
"""
base_sync_all.py - 批量同步所有 Base 数据
"""

import subprocess
import json
from pathlib import Path

def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

REPO_ROOT = _find_repo_root()
DATA_DIR = REPO_ROOT / "workspace" / "knowledge" / "data"

BASE_CONFIG = {
    "mcn": "SZ1Cb3RbbabNJLsr6TpcJPEfn2g",
    "brand-ops": "J99JbkE9eaEK97sMGfEcSG8UnLd",
    "kol-incubation": "LTLNbBlGTaB4mNs6by0cvhPhnib",
    "live-commerce": "KFnUbyA0jaSXcrsHuENcY9gBnJe",
    "private-domain": "WKOXb2zm7a1XIFseYMmcYl4znJn",
    "short-video": "X8o0b9M9ZaSk0asVcr4ceF16neg",
    "virtual-ip": "FeyIbsjrNa7pPksOqXmcE7ZMnff",
}

def run_cmd(args):
    result = subprocess.run(
        ["lark-cli"] + args,
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0:
        print(f"❌ {result.stderr[:200]}")
        return None
    return json.loads(result.stdout)

def sync_table(base_token, table_name, output_dir):
    print(f"  📊 {table_name}...", end=" ")
    records = run_cmd([
        "base", "+record-list",
        "--base-token", base_token,
        "--table-id", table_name,
        "--as", "user", "--profile", "compass",
        "--limit", "500"
    ])
    if not records or not records.get("ok"):
        print("失败")
        return 0
    
    output_dir.mkdir(parents=True, exist_ok=True)
    import re
    safe_name = re.sub(r'[^\w]', '_', table_name)
    from datetime import datetime
    output_file = output_dir / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    count = len(records.get('data', {}).get('data', []))
    print(f"✓ {count}条")
    return count

def sync_base(base_name, base_token):
    print(f"\n🔷 {base_name} ({base_token})")
    
    # 获取表格列表
    tables = run_cmd([
        "base", "+table-list",
        "--base-token", base_token,
        "--as", "user", "--profile", "compass"
    ])
    
    if not tables or not tables.get("ok"):
        print(f"  ❌ 无法获取表格列表")
        return
    
    table_list = tables.get('data', {}).get('tables', [])
    print(f"  发现 {len(table_list)} 个表格")
    
    output_dir = DATA_DIR / base_name
    total = 0
    for table in table_list:
        count = sync_table(base_token, table['name'], output_dir)
        total += count
    
    print(f"  ✅ 总计: {total} 条记录")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 同步指定 base
        base_name = sys.argv[1]
        base_token = sys.argv[2] if len(sys.argv) > 2 else BASE_CONFIG.get(base_name)
        if base_token:
            sync_base(base_name, base_token)
        else:
            print(f"❌ 未知 base: {base_name}")
    else:
        # 同步所有已知 base
        for name, token in BASE_CONFIG.items():
            if token:
                sync_base(name, token)
            else:
                print(f"\n⏭️ {name}: token 未配置，跳过")
