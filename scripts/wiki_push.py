#!/usr/bin/env python3
"""
Wiki 文档推送脚本
将本地 Markdown 文件批量推送到飞书 Wiki 知识库。

用法:
    python scripts/wiki_push.py --space <space_id> --parent <parent_node_token> --dir <local_dir>
    python scripts/wiki_push.py --space 7527651943557578771 --parent DiPHw4MW2icKoAk4X0DcVx69nOf --dir "docs/MCN lark"

环境变量:
    FEISHU_APP_ID, FEISHU_APP_SECRET
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def run_lark_cli(args: list) -> dict:
    """运行 lark-cli 命令并返回 JSON 结果。"""
    cmd = ["lark-cli"] + args + ["--format", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return {"ok": False, "error": result.stderr}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # 可能有 warning 行，找 JSON 开始位置
        text = result.stdout
        idx = text.find("{")
        if idx >= 0:
            return json.loads(text[idx:])
        return {"ok": False, "error": "Invalid JSON output"}


def create_docx(title: str, content: str) -> str:
    """创建飞书 docx 文档，返回 obj_token。"""
    # 先创建空文档获取 token
    resp = run_lark_cli([
        "docx", "documents", "create",
        "--data", json.dumps({"title": title})
    ])
    if not resp.get("code") == 0:
        print(f"创建文档失败: {resp}", file=sys.stderr)
        return ""
    doc_token = resp["data"]["document"]["document_id"]

    # 写入内容（简化版：直接通过 blocks 写入文本）
    blocks = markdown_to_blocks(content)
    for block in blocks:
        run_lark_cli([
            "docx", "documents", "blocks", "create",
            "--params", json.dumps({"document_id": doc_token}),
            "--data", json.dumps({"children": [block]})
        ])

    return doc_token


def markdown_to_blocks(md: str) -> list:
    """将 Markdown 简单转为飞书 docx block 列表。"""
    blocks = []
    lines = md.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            blocks.append({"block_type": 1, "heading1": {"elements": [{"text_run": {"content": line[2:]}}]}})
        elif line.startswith("## "):
            blocks.append({"block_type": 2, "heading2": {"elements": [{"text_run": {"content": line[3:]}}]}})
        elif line.startswith("### "):
            blocks.append({"block_type": 3, "heading3": {"elements": [{"text_run": {"content": line[4:]}}]}})
        elif line.startswith("- "):
            blocks.append({"block_type": 12, "bulleted": {"elements": [{"text_run": {"content": line[2:]}}]}})
        elif re.match(r"^\d+\. ", line):
            blocks.append({"block_type": 13, "ordered": {"elements": [{"text_run": {"content": re.sub(r"^\d+\. ", "", line)}}]}})
        elif line.startswith("| ") and " | " in line:
            # 表格行，跳过表头分隔符
            if not re.match(r"^\|[-\s|]+\|$", line):
                cells = [c.strip() for c in line.strip("|").split("|")]
                blocks.append({"block_type": 21, "table": {"property": {}, "children": []}})
        else:
            blocks.append({"block_type": 4, "text": {"elements": [{"text_run": {"content": line}}]}})
    return blocks


def mount_to_wiki(doc_token: str, space_id: str, parent_token: str, title: str) -> str:
    """将文档挂载到 Wiki 节点下，返回 wiki_node_token。"""
    resp = run_lark_cli([
        "wiki", "nodes", "create",
        "--data", json.dumps({
            "space_id": space_id,
            "parent_node_token": parent_token,
            "node_type": "origin",
            "obj_type": "docx",
            "obj_token": doc_token,
            "title": title
        })
    ])
    if resp.get("code") == 0:
        return resp["data"]["node"]["node_token"]
    print(f"挂载 Wiki 失败: {resp}", file=sys.stderr)
    return ""


def push_local_dir(space_id: str, parent_token: str, local_dir: str):
    """批量推送本地目录下的 Markdown 文件到 Wiki。"""
    dir_path = Path(local_dir)
    if not dir_path.exists():
        print(f"目录不存在: {local_dir}", file=sys.stderr)
        return

    files = sorted(dir_path.glob("*.md")) + sorted(dir_path.glob("*"))
    files = [f for f in files if f.is_file() and not f.name.endswith(".tmp")]

    print(f"发现 {len(files)} 个文件，开始推送...")
    for f in files:
        title = f.stem
        content = f.read_text(encoding="utf-8")
        print(f"\n📄 处理: {title}")

        doc_token = create_docx(title, content)
        if not doc_token:
            continue

        node_token = mount_to_wiki(doc_token, space_id, parent_token, title)
        if node_token:
            print(f"✅ 成功: {title} -> wiki_node_token={node_token}")
        else:
            print(f"⚠️ 文档已创建但未挂载: {title} -> doc_token={doc_token}")


def main():
    parser = argparse.ArgumentParser(description="推送本地 Markdown 到飞书 Wiki")
    parser.add_argument("--space", required=True, help="Wiki 空间 ID")
    parser.add_argument("--parent", required=True, help="父节点 token")
    parser.add_argument("--dir", required=True, help="本地目录路径")
    args = parser.parse_args()

    push_local_dir(args.space, args.parent, args.dir)


if __name__ == "__main__":
    main()
