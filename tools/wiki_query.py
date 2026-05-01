#!/usr/bin/env python3
"""
Compass Wiki Query — 基于结构化知识底座的问答检索

基于 llm-wiki-agent 的 query.py 轻量改造：
- 不使用向量数据库，通过关键词匹配 + 图邻居扩展检索相关页面
- 保留飞书原始链接引用（从 source page frontmatter 提取 lark_url）
- 封装为函数，供 qa-bot Agent 直接调用
- 使用 Compass 配置的 Moonshot API

Usage:
    python tools/wiki_query.py "垂类达人孵化的粉丝增长率为什么下滑？"
    python tools/wiki_query.py "达人筛选标准有哪些硬性指标？" --save
    python tools/wiki_query.py "整改方案有哪些行动项？" --save syntheses/整改方案分析.md

API:
    from tools.wiki_query import query_wiki
    result = query_wiki("问题", project_scope="垂类达人孵化")
    # result = {"answer": "...", "sources": [...], "related_pages": [...]}
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
GRAPH_JSON = REPO_ROOT / "graph" / "graph.json"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


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


def extract_lark_url_from_page(page_path: Path) -> str:
    """从 wiki 页面中提取飞书原始链接"""
    content = read_file(page_path)
    fm, _ = extract_frontmatter(content)
    url = fm.get("lark_url", "")
    if not url:
        # 尝试从内容中匹配
        match = re.search(r"https://[\w\-]+\.feishu\.cn/[\w/]+", content)
        if match:
            url = match.group()
    return url


def call_llm(prompt: str, max_tokens: int = 4096) -> str:
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
    print(f"  saved: {path.relative_to(REPO_ROOT)}")


def find_relevant_pages(question: str, project_scope: str | None = None) -> list[Path]:
    """通过关键词匹配 + 图邻居扩展找到相关页面

    Args:
        question: 用户问题
        project_scope: 项目范围过滤（如"垂类达人孵化"），None 表示不限
    """
    index_content = read_file(INDEX_FILE)
    if not index_content:
        return []

    # Step 1: 从 index.md 中关键词匹配相关页面
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', index_content)
    question_lower = question.lower()
    if project_scope:
        question_lower = f"{question_lower} {project_scope.lower()}"

    relevant = []
    for title, href in md_links:
        title_lower = title.lower()
        has_cjk = any('一' <= ch <= '鿿' for ch in title)

        if has_cjk:
            # CJK: 检查标题中任意 2 字组合是否出现在问题中
            matched = any(
                title_lower[j:j+2] in question_lower
                for j in range(len(title_lower) - 1)
                if any('一' <= c <= '鿿' for c in title_lower[j:j+2])
            )
        else:
            # Latin: 词级匹配
            matched = any(word in question_lower for word in title_lower.split() if len(word) > 2)

        # 项目范围过滤
        if project_scope and not matched:
            # 如果标题包含项目名，也视为相关
            matched = project_scope.lower() in title_lower

        if matched:
            p = WIKI_DIR / href
            if p.exists() and p not in relevant:
                relevant.append(p)

    # Step 2: 图邻居扩展
    if GRAPH_JSON.exists() and relevant:
        try:
            graph_data = json.loads(GRAPH_JSON.read_text())
            page_ids = {p.relative_to(WIKI_DIR).as_posix().replace('.md', '') for p in relevant}
            neighbors = set()
            for edge in graph_data.get('edges', []):
                if edge.get('confidence', 0) >= 0.7:
                    if edge['from'] in page_ids:
                        neighbors.add(edge['to'])
                    elif edge['to'] in page_ids:
                        neighbors.add(edge['from'])
            for nid in neighbors:
                np = WIKI_DIR / f"{nid}.md"
                if np.exists() and np not in relevant:
                    relevant.append(np)
        except (json.JSONDecodeError, KeyError):
            pass

    # Step 3: 总是包含 overview
    overview = WIKI_DIR / "overview.md"
    if overview.exists() and overview not in relevant:
        relevant.insert(0, overview)

    return relevant[:15]  # 限制避免上下文溢出


def llm_select_pages(question: str, index_content: str) -> list[Path]:
    """当关键词匹配不足时，用 LLM 从索引中选择相关页面"""
    prompt = f"""给定以下知识库索引：

{index_content}

哪些页面最有助于回答这个问题："{question}"

请只返回一个 JSON 数组，包含相对文件路径（如索引中列出的），例如：["sources/foo.md", "concepts/Bar.md"]。最多 10 个页面。"""
    raw = call_llm(prompt, max_tokens=512)
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        paths = json.loads(raw)
        return [WIKI_DIR / p for p in paths if (WIKI_DIR / p).exists()]
    except (json.JSONDecodeError, TypeError):
        return []


def build_sources_citation(pages: list[Path]) -> list[dict]:
    """构建来源引用信息列表"""
    sources = []
    for p in pages:
        rel = p.relative_to(WIKI_DIR)
        content = read_file(p)
        fm, body = extract_frontmatter(content)

        # 提取标题
        title = fm.get("title", p.stem)
        if not title or title == p.stem:
            title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()

        lark_url = fm.get("lark_url", "")
        if not lark_url:
            lark_url = extract_lark_url_from_page(p)

        sources.append({
            "title": title,
            "wiki_path": str(rel),
            "lark_url": lark_url,
            "preview": body[:200].replace('\n', ' ') + "...",
        })
    return sources


def query_wiki(question: str, project_scope: str | None = None, save_path: str | None = None) -> dict:
    """查询 Compass 知识库

    Args:
        question: 用户问题
        project_scope: 项目范围（如"垂类达人孵化"），用于权限过滤
        save_path: 可选，保存答案到指定 wiki 路径

    Returns:
        dict: {
            "answer": "Markdown 格式答案",
            "sources": [{"title": "...", "wiki_path": "...", "lark_url": "..."}],
            "related_pages": ["wiki/sources/xxx.md", ...],
            "saved_to": "wiki/syntheses/xxx.md" | None
        }
    """
    today = date.today().isoformat()

    # Step 1: 读取索引
    index_content = read_file(INDEX_FILE)
    if not index_content:
        return {
            "answer": "知识库为空。请先使用 wiki_ingest.py 导入文档。",
            "sources": [],
            "related_pages": [],
            "saved_to": None,
        }

    # Step 2: 找到相关页面
    relevant_pages = find_relevant_pages(question, project_scope)

    if not relevant_pages or len(relevant_pages) <= 1:
        print("  通过 LLM 选择相关页面...")
        relevant_pages = llm_select_pages(question, index_content)

    # Step 3: 读取相关页面内容
    pages_context = ""
    for p in relevant_pages:
        rel = p.relative_to(REPO_ROOT)
        content = p.read_text(encoding="utf-8")
        pages_context += f"\n\n### {rel}\n{content}"

    if not pages_context:
        pages_context = f"\n\n### wiki/index.md\n{index_content}"

    # Step 4: 综合答案
    print(f"  从 {len(relevant_pages)} 个页面综合答案...")

    scope_hint = f"\n当前查询范围：{project_scope}" if project_scope else ""

    prompt = f"""你是 Compass（司南）MCN 事业部的知识问答助手。请基于以下知识库页面回答问题。

回答要求：
1. 使用 Markdown 格式，结构清晰
2. 关键事实必须标注来源，使用 [[PageName]] 的 wikilink 语法
3. 如果涉及飞书原始文档，在 Sources 部分提供链接
4. 如果知识库中没有相关信息，明确说明"根据现有资料，暂未找到相关信息"
5. 不要编造数据中不存在的信息
{scope_hint}

知识库页面：
{pages_context}

问题：{question}

请给出结构化的回答，包含标题、要点和 Sources 引用部分。"""

    answer = call_llm(prompt, max_tokens=4096)

    # Step 5: 构建来源引用
    sources = build_sources_citation(relevant_pages)

    # Step 6: 可选保存
    saved_to = None
    if save_path is not None:
        if save_path == "":
            slug = input("\n保存为（slug，如 '整改方案分析'）: ").strip()
            if not slug:
                print("跳过保存。")
            else:
                save_path = f"syntheses/{slug}.md"

        if save_path:
            full_save_path = WIKI_DIR / save_path
            frontmatter = f"""---
title: "{question[:80]}"
type: synthesis
tags: []
sources: []
last_updated: {today}
---

"""
            write_file(full_save_path, frontmatter + answer)

            # 更新索引
            index_content = read_file(INDEX_FILE)
            entry = f"- [{question[:60]}]({save_path}) — 综合"
            if "## Syntheses" in index_content:
                index_content = index_content.replace("## Syntheses\n", f"## Syntheses\n{entry}\n")
                INDEX_FILE.write_text(index_content, encoding="utf-8")
            saved_to = str(full_save_path.relative_to(REPO_ROOT))

    # Step 7: 追加日志
    log_entry = f"## [{today}] query | {question[:80]}\n\n综合了 {len(relevant_pages)} 个页面的答案。"
    if saved_to:
        log_entry += f" 保存到 {saved_to}。"
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(log_entry + "\n\n" + existing, encoding="utf-8")

    return {
        "answer": answer,
        "sources": sources,
        "related_pages": [str(p.relative_to(WIKI_DIR)) for p in relevant_pages],
        "saved_to": saved_to,
    }


def main():
    parser = argparse.ArgumentParser(description="Query the Compass Wiki")
    parser.add_argument("question", help="Question to ask the wiki")
    parser.add_argument("--scope", default=None, help="Project scope filter (e.g. '垂类达人孵化')")
    parser.add_argument("--save", nargs="?", const="", default=None,
                        help="Save answer to wiki (optionally specify path)")
    args = parser.parse_args()

    result = query_wiki(args.question, project_scope=args.scope, save_path=args.save)

    print("\n" + "=" * 60)
    print(result["answer"])
    print("=" * 60)

    if result["sources"]:
        print("\n📚 Sources:")
        for s in result["sources"]:
            url_hint = f" → {s['lark_url']}" if s["lark_url"] else ""
            print(f"  • [[{s['title']}]] ({s['wiki_path']}){url_hint}")

    if result["saved_to"]:
        print(f"\n💾 Saved to: {result['saved_to']}")


if __name__ == "__main__":
    main()
