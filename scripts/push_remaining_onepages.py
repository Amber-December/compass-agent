#!/usr/bin/env python3
"""推送剩余 5 个项目的 OnePage 到飞书 Wiki"""

import json
import subprocess
from pathlib import Path

PROFILE = "compass"
SPACE_ID = "7634845410292403395"
PARENT_NODE = "WMXewXyeYi62dTk3p5xct3yZnde"

PROJECTS = [
    "短视频内容矩阵",
    "品牌代运营",
    "直播电商",
    "达人私域运营",
    "虚拟IP孵化与运营",
]

BASE_DIR = Path("/Users/amber/compass-agent/docs/projects")


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
    for project in PROJECTS:
        md_file = BASE_DIR / project / "项目 OnePage.md"
        if not md_file.exists():
            print(f"⚠️ 文件不存在: {md_file}")
            continue

        print(f"\n📄 {project}")
        obj_token = create_wiki_node(PARENT_NODE, project)
        if obj_token:
            update_doc_content(obj_token, md_file)

    print("\n🎉 全部完成！")


if __name__ == "__main__":
    main()
