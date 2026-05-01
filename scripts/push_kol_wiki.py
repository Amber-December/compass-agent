#!/usr/bin/env python3
"""
将垂类达人孵化项目的本地文档批量推送到飞书 Wiki

节点结构:
垂类达人孵化 (HtoHwS0U8iaZYokYXmNcFUGpnkB)
├── 项目 OnePage (Nc6EwRimJirsREkOKA5cOM25n8t)
├── 周报归档 (KvSJwb8byi7QK3kwHwtcVIcYnBK)
│   ├── Week 1-9 周报
├── 会议纪要 (EuRow7CAOiut4Kk7uybcGLDHnbd)
│   ├── 9 份会议纪要
├── 项目文档 (DoQwwmHElitW8Qk85yLcr051nlf)
│   ├── 3 份项目文档
└── 数据看板 (GlDvwoh3CiEmtjketV5cebHqnne)
"""

import json
import subprocess
from pathlib import Path

PROFILE = "compass"
SPACE_ID = "7634845410292403395"
PARENT_NODES = {
    "周报归档": "KvSJwb8byi7QK3kwHwtcVIcYnBK",
    "会议纪要": "EuRow7CAOiut4Kk7uybcGLDHnbd",
    "项目文档": "DoQwwmHElitW8Qk85yLcr051nlf",
    "数据看板": "GlDvwoh3CiEmtjketV5cebHqnne",
    "项目 OnePage": "Nc6EwRimJirsREkOKA5cOM25n8t",
}

BASE_DIR = Path("/Users/amber/lark-knowledge-agent/docs/projects/垂类达人孵化")


def run_cmd(cmd: list) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return {"ok": False, "error": result.stderr}
    try:
        text = result.stdout
        idx = text.find("{")
        if idx >= 0:
            return json.loads(text[idx:])
        return {"ok": False, "error": "No JSON"}
    except json.JSONDecodeError:
        return {"ok": False, "error": "Invalid JSON"}


def create_wiki_node(parent_token: str, title: str) -> str:
    """创建 wiki 节点，返回 obj_token"""
    cmd = [
        "lark-cli", "wiki", "+node-create",
        f"--profile={PROFILE}", "--as", "bot",
        f"--space-id={SPACE_ID}",
        f"--parent-node-token={parent_token}",
        "--obj-type", "docx",
        "--title", title,
    ]
    resp = run_cmd(cmd)
    if resp.get("ok"):
        return resp["data"]["obj_token"]
    print(f"  ❌ 创建失败: {title} -> {resp}")
    return ""


def update_doc_content(doc_token: str, md_file: Path):
    """将 Markdown 内容写入飞书文档"""
    content = md_file.read_text(encoding="utf-8")
    cmd = [
        "lark-cli", "docs", "+update",
        f"--profile={PROFILE}", "--as", "bot",
        "--doc", doc_token,
        "--mode", "overwrite",
        "--markdown", "-",
    ]
    result = subprocess.run(cmd, input=content, capture_output=True, text=True, encoding="utf-8")
    try:
        text = result.stdout
        idx = text.find("{")
        if idx >= 0:
            resp = json.loads(text[idx:])
        else:
            resp = {"ok": False}
    except json.JSONDecodeError:
        resp = {"ok": False}

    if resp.get("ok"):
        print(f"    ✅ 内容写入成功")
    else:
        print(f"    ❌ 内容写入失败: {resp}")


def main():
    # 1. 项目 OnePage
    one_page_file = BASE_DIR / "项目 OnePage.md"
    if one_page_file.exists():
        print(f"📄 项目 OnePage -> {PARENT_NODES['项目 OnePage']}")
        update_doc_content(PARENT_NODES["项目 OnePage"], one_page_file)

    # 2. 周报归档
    weekly_dir = BASE_DIR / "周报归档"
    if weekly_dir.exists():
        print(f"\n📁 周报归档")
        for md_file in sorted(weekly_dir.glob("*.md")):
            title = md_file.stem
            print(f"  📄 {title}")
            obj_token = create_wiki_node(PARENT_NODES["周报归档"], title)
            if obj_token:
                update_doc_content(obj_token, md_file)

    # 3. 会议纪要
    minutes_dir = BASE_DIR / "会议纪要"
    if minutes_dir.exists():
        print(f"\n📁 会议纪要")
        for md_file in sorted(minutes_dir.glob("*.md")):
            title = md_file.stem
            print(f"  📄 {title}")
            obj_token = create_wiki_node(PARENT_NODES["会议纪要"], title)
            if obj_token:
                update_doc_content(obj_token, md_file)

    # 4. 项目文档
    docs_dir = BASE_DIR / "项目文档"
    if docs_dir.exists():
        print(f"\n📁 项目文档")
        for md_file in sorted(docs_dir.glob("*.md")):
            title = md_file.stem
            print(f"  📄 {title}")
            obj_token = create_wiki_node(PARENT_NODES["项目文档"], title)
            if obj_token:
                update_doc_content(obj_token, md_file)

    # 5. 数据看板
    dashboard_dir = BASE_DIR / "数据看板"
    if dashboard_dir.exists():
        print(f"\n📁 数据看板")
        for md_file in sorted(dashboard_dir.glob("*.md")):
            title = md_file.stem
            print(f"  📄 {title}")
            obj_token = create_wiki_node(PARENT_NODES["数据看板"], title)
            if obj_token:
                update_doc_content(obj_token, md_file)

    print("\n🎉 全部完成！")


if __name__ == "__main__":
    main()
