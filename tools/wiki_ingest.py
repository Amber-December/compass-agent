#!/usr/bin/env python3
"""
Compass Wiki Ingest — 将飞书文档编译为结构化知识底座

基于 llm-wiki-agent 的 ingest.py 轻量改造：
- 输入从 raw/ 改为 workspace/raw_lark/
- 保留飞书原始 URL（从 frontmatter 的 lark_url 或文件名映射表读取）
- 使用 Compass 配置的 Moonshot API
- 适配 MCN 事业部场景

Usage:
    python tools/wiki_ingest.py workspace/raw_lark/wiki/垂类达人孵化/项目\ OnePage.md
    python tools/wiki_ingest.py workspace/raw_lark/wiki/垂类达人孵化/周报归档/
    python tools/wiki_ingest.py --validate-only
    python tools/wiki_ingest.py --batch workspace/raw_lark/wiki/

输出：
    wiki/sources/<slug>.md      — 结构化来源页
    wiki/entities/<Name>.md     — 实体页（人、项目、品牌）
    wiki/concepts/<Name>.md     — 概念页（SOP、方法论）
    wiki/index.md               — 自动更新索引
    wiki/overview.md            — 自动更新全局综合
    wiki/log.md                 — 操作日志
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import date
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
LOG_FILE = WIKI_DIR / "log.md"
INDEX_FILE = WIKI_DIR / "index.md"
OVERVIEW_FILE = WIKI_DIR / "overview.md"
RAW_LARK_DIR = REPO_ROOT / "workspace" / "raw_lark"
SCHEMA_FILE = REPO_ROOT / "agents" / "wiki-manager" / "docs" / "project-wiki-structure.md"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def call_llm(prompt: str, max_tokens: int = 8192) -> str:
    """调用 Compass 配置的 LLM（Moonshot / Kimi）"""
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai not installed. Run: pip install openai")
        sys.exit(1)

    api_key = os.getenv("MOONSHOT_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "https://api.kimi.com/coding/")
    model = os.getenv("LLM_MODEL", "kimi-k2-6")

    if not api_key:
        # fallback to openclaw config
        import json as _json
        oc_config = REPO_ROOT / "openclaw.json"
        if oc_config.exists():
            cfg = _json.loads(oc_config.read_text())
            api_key = cfg.get("llm", {}).get("apiKey", "")
            if api_key.startswith("${"):
                api_key = os.getenv(api_key.strip("${}"), "")
            base_url = cfg.get("llm", {}).get("baseURL", base_url)
            model = cfg.get("llm", {}).get("model", model)

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote: {path.relative_to(REPO_ROOT)}")


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """提取 YAML frontmatter 和正文"""
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if match:
        fm_text, body = match.group(1), match.group(2)
        try:
            import yaml
            return yaml.safe_load(fm_text) or {}, body
        except ImportError:
            return {}, content
    return {}, content


def extract_lark_url(content: str, default: str = "") -> str:
    """从 frontmatter 或内容中提取飞书 URL"""
    fm, _ = extract_frontmatter(content)
    url = fm.get("lark_url", "")
    if not url:
        # 尝试从内容中匹配飞书 URL
        match = re.search(r"https://[\w\-]+\.feishu\.cn/[\w/]+", content)
        if match:
            url = match.group()
    return url or default


def build_wiki_context() -> str:
    """构建当前 wiki 状态的上下文"""
    parts = []
    if INDEX_FILE.exists():
        parts.append(f"## wiki/index.md\n{read_file(INDEX_FILE)}")
    if OVERVIEW_FILE.exists():
        parts.append(f"## wiki/overview.md\n{read_file(OVERVIEW_FILE)}")
    # 包含最近 5 个 source pages 用于矛盾检测
    sources_dir = WIKI_DIR / "sources"
    if sources_dir.exists():
        recent = sorted(sources_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        for p in recent:
            parts.append(f"## {p.relative_to(REPO_ROOT)}\n{p.read_text()}")
    return "\n\n---\n\n".join(parts)


def parse_json_from_response(text: str) -> dict:
    """从 LLM 响应中解析 JSON"""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in response")
    return json.loads(match.group())


def update_index(new_entry: str, section: str = "Sources"):
    """更新 wiki/index.md"""
    content = read_file(INDEX_FILE)
    if not content:
        content = "# Compass 知识库索引\n\n> 司南（Compass）MCN 事业部知识底座 — 由 wiki-manager Agent 自动维护\n\n## Overview\n- [Overview](overview.md) — 跨项目知识综合\n\n## Sources\n\n## Entities\n\n## Concepts\n\n## Syntheses\n"
    section_header = f"## {section}"
    if section_header in content:
        # 避免重复条目
        if new_entry.strip() not in content:
            content = content.replace(section_header + "\n", section_header + "\n" + new_entry + "\n")
    else:
        content += f"\n{section_header}\n{new_entry}\n"
    write_file(INDEX_FILE, content)


def append_log(entry: str):
    """追加到 wiki/log.md"""
    existing = read_file(LOG_FILE)
    write_file(LOG_FILE, entry.strip() + "\n\n" + existing)


def extract_wikilinks(content: str) -> list[str]:
    """提取所有 [[WikiLink]]"""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def all_wiki_pages() -> set[str]:
    """返回所有 wiki 页面的 stem（小写）"""
    pages = set()
    for p in WIKI_DIR.rglob("*.md"):
        if p.name not in ("index.md", "log.md", "lint-report.md"):
            pages.add(p.stem.lower())
    return pages


def validate_ingest(changed_pages: list[str] | None = None) -> dict:
    """验证 wiki 完整性"""
    existing_pages = all_wiki_pages()
    index_content = read_file(INDEX_FILE).lower()

    if changed_pages:
        scan_paths = [WIKI_DIR / p for p in changed_pages if (WIKI_DIR / p).exists()]
    else:
        scan_paths = [p for p in WIKI_DIR.rglob("*.md")
                      if p.name not in ("index.md", "log.md", "lint-report.md")]

    broken_links = []
    for page_path in scan_paths:
        content = read_file(page_path)
        rel = str(page_path.relative_to(WIKI_DIR))
        for link in extract_wikilinks(content):
            link_stem = Path(link).stem.lower() if '/' in link else link.lower()
            if link_stem not in existing_pages:
                broken_links.append((rel, link))

    unindexed = []
    for p in (changed_pages or []):
        page_path = WIKI_DIR / p
        if page_path.exists():
            stem = page_path.stem.lower()
            if stem not in index_content and p not in ("log.md", "overview.md"):
                unindexed.append(p)

    return {"broken_links": broken_links, "unindexed": unindexed}


def make_slug(title: str) -> str:
    """将标题转换为 kebab-case slug"""
    # 先替换常见中文标点
    t = title.replace("（", " ").replace("）", " ").replace("[", " ").replace("]", " ")
    t = re.sub(r'[^\w\s-]', '', t)
    t = re.sub(r'[-\s]+', '-', t)
    return t.strip('-').lower()[:80]


def ingest(source_path: str):
    """ingest 单个源文档"""
    source = Path(source_path)
    if not source.exists():
        print(f"Error: file not found: {source_path}")
        return

    if source.suffix.lower() != ".md":
        print(f"  ⚠️  跳过非 Markdown 文件: {source.name}")
        return

    source_content = source.read_text(encoding="utf-8")
    source_hash = sha256(source_content)
    today = date.today().isoformat()

    print(f"\nIngesting: {source.name}  (hash: {source_hash})")

    # 提取飞书 URL
    lark_url = extract_lark_url(source_content)

    wiki_context = build_wiki_context()
    schema = read_file(SCHEMA_FILE)

    prompt = f"""你正在维护 Compass（司南）MCN 事业部的知识库。请处理以下飞书文档，将其知识提取并整合到知识库中。

知识库维护规范：
- 每份来源文档在 wiki/sources/ 中创建结构化摘要页
- 自动提取关键人物、项目、品牌创建实体页（wiki/entities/）
- 自动提取方法论、规范、流程创建概念页（wiki/concepts/）
- 使用 [[Wikilink]] 语法在文本中创建交叉引用
- 保留飞书原始链接供引用

当前知识库状态：
{wiki_context if wiki_context else "(知识库为空 — 这是第一个来源)"}

新来源文档（文件: {source.name}）:
=== SOURCE START ===
{source_content}
=== SOURCE END ===

飞书原始链接: {lark_url or "未提供"}

今天日期: {today}

请返回一个有效的 JSON 对象，包含以下字段（不要输出 markdown 代码块外的内容）：
{{
  "title": "人类可读的标题",
  "slug": "kebab-case-slug-用于文件名",
  "source_page": "wiki/sources/<slug>.md 的完整 markdown 内容 — 使用来源页格式。关键要求：积极将关键人物、产品、概念和项目转换为 [[Wikilink]] 内联链接。",
  "index_entry": "- [标题](sources/slug.md) — 一句话摘要",
  "overview_update": "wiki/overview.md 的完整更新内容，或 null 如果不需要更新",
  "entity_pages": [
    {{"path": "entities/EntityName.md", "content": "完整 markdown 内容"}}
  ],
  "concept_pages": [
    {{"path": "concepts/ConceptName.md", "content": "完整 markdown 内容"}}
  ],
  "contradictions": ["描述与现有知识库内容的任何矛盾，或空列表"],
  "log_entry": "## [{today}] ingest | <标题>\\n\\nAdded source. Key claims: ..."
}}
"""

    print(f"  calling LLM...")
    raw = call_llm(prompt, max_tokens=8192)
    try:
        data = parse_json_from_response(raw)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing API response: {e}")
        debug_path = REPO_ROOT / "workspace" / "ingest_debug.json"
        debug_path.write_text(raw, encoding="utf-8")
        print(f"  Raw response saved to {debug_path}")
        return

    # 写入 source page（附加飞书 URL frontmatter）
    slug = data["slug"]
    source_page_content = data["source_page"]
    if lark_url and "lark_url:" not in source_page_content:
        source_page_content = f"---\nlark_url: {lark_url}\nsource_file: {source.name}\ningest_date: {today}\n---\n\n" + source_page_content
    write_file(WIKI_DIR / "sources" / f"{slug}.md", source_page_content)

    # 写入实体页
    for page in data.get("entity_pages", []):
        write_file(WIKI_DIR / page["path"], page["content"])

    # 写入概念页
    for page in data.get("concept_pages", []):
        write_file(WIKI_DIR / page["path"], page["content"])

    # 更新 overview
    if data.get("overview_update"):
        write_file(OVERVIEW_FILE, data["overview_update"])

    # 更新 index
    update_index(data["index_entry"], section="Sources")

    # 追加 log
    append_log(data["log_entry"])

    # 报告矛盾
    contradictions = data.get("contradictions", [])
    if contradictions:
        print("\n  ⚠️  检测到矛盾:")
        for c in contradictions:
            print(f"     - {c}")

    # 验证
    created_pages = [f"sources/{slug}.md"]
    for page in data.get("entity_pages", []):
        created_pages.append(page["path"])
    for page in data.get("concept_pages", []):
        created_pages.append(page["path"])
    updated_pages = ["index.md", "log.md"]
    if data.get("overview_update"):
        updated_pages.append("overview.md")

    validation = validate_ingest(created_pages)

    print(f"\n{'='*50}")
    print(f"  ✅ Ingested: {data['title']}")
    print(f"{'='*50}")
    print(f"  Created : {len(created_pages)} pages")
    for p in created_pages:
        print(f"           + wiki/{p}")
    print(f"  Updated : {len(updated_pages)} pages")
    for p in updated_pages:
        print(f"           ~ wiki/{p}")
    if contradictions:
        print(f"  Warnings: {len(contradictions)} contradiction(s)")
    if validation["broken_links"]:
        print(f"  ⚠️  Broken links: {len(validation['broken_links'])}")
        for page, link in validation["broken_links"][:10]:
            print(f"           wiki/{page} → [[{link}]]")
    if validation["unindexed"]:
        print(f"  ⚠️  Not in index.md: {len(validation['unindexed'])}")
    if not validation["broken_links"] and not validation["unindexed"]:
        print("  ✓ Validation passed")
    print()


def batch_ingest(dir_path: str):
    """批量 ingest 目录下的所有 Markdown 文件"""
    target = Path(dir_path)
    if not target.exists():
        print(f"Error: directory not found: {dir_path}")
        return

    md_files = list(target.rglob("*.md"))
    if not md_files:
        print(f"No .md files found in {dir_path}")
        return

    print(f"Batch mode: found {len(md_files)} files to ingest.\n")
    for f in sorted(md_files):
        ingest(str(f))


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--validate-only":
        print("Running wiki validation (no ingest)...\n")
        result = validate_ingest()
        if result["broken_links"]:
            print(f"Broken wikilinks: {len(result['broken_links'])}")
            for page, link in result["broken_links"][:20]:
                print(f"  wiki/{page} → [[{link}]]")
        else:
            print("No broken wikilinks found.")
        print()
        pages = all_wiki_pages()
        index_content = read_file(INDEX_FILE).lower()
        unindexed_all = []
        for p in WIKI_DIR.rglob("*.md"):
            if p.name in ("index.md", "log.md", "lint-report.md", "overview.md"):
                continue
            if p.stem.lower() not in index_content:
                unindexed_all.append(str(p.relative_to(WIKI_DIR)))
        if unindexed_all:
            print(f"Pages not in index.md: {len(unindexed_all)}")
            for up in unindexed_all[:20]:
                print(f"  wiki/{up}")
        else:
            print("All pages are indexed.")
        return

    if len(sys.argv) == 3 and sys.argv[1] == "--batch":
        batch_ingest(sys.argv[2])
        return

    if len(sys.argv) < 2:
        print("Usage: python tools/wiki_ingest.py <path-to-source.md>")
        print("       python tools/wiki_ingest.py <directory/>")
        print("       python tools/wiki_ingest.py --batch <directory/>")
        print("       python tools/wiki_ingest.py --validate-only")
        sys.exit(1)

    target = Path(sys.argv[1])
    if target.is_dir():
        batch_ingest(sys.argv[1])
    elif target.is_file():
        ingest(sys.argv[1])
    else:
        print(f"Error: path not found: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
