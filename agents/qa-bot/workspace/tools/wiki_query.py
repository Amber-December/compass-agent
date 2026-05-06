#!/usr/bin/env python3
"""
Compass QA-Bot Wiki Query — 知识库检索工具（配合 OpenClaw LLM Skill 使用）

功能：
- 根据用户问题和 scope，检索相关知识库页面
- 返回页面内容和元数据，供 OpenClaw LLM 综合生成回答
- 不直接调用 LLM API，只做数据检索

Usage:
    python tools/wiki_query.py "垂类达人孵化的粉丝增长率" --scope kol-incubation
    
API:
    from tools.wiki_query import query_wiki, query_graph, personal_intro
    result = query_wiki("问题", scope="kol-incubation")
    # result = {"pages": [...], "context": "...", "sources": [...]}
"""

import os
import sys
import re
import json
import argparse
import webbrowser
from pathlib import Path
from datetime import date

def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

REPO_ROOT = _find_repo_root()
WIKI_DIR = REPO_ROOT / "workspace" / "knowledge" / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
GRAPH_JSON = REPO_ROOT / "workspace" / "knowledge" / "graph" / "graph.json"
GRAPH_HTML = REPO_ROOT / "workspace" / "knowledge" / "graph" / "graph.html"

# 权限范围映射
SCOPE_PATH_MAP = {
    None: [""],
    "public": ["public/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
    "dept": ["public/", "dept/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
    "kol-incubation": ["public/", "dept/", "projects/kol-incubation/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
    "brand-ops": ["public/", "dept/", "projects/brand-ops/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
    "live-commerce": ["public/", "dept/", "projects/live-commerce/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
    "short-video": ["public/", "dept/", "projects/short-video/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
    "private-domain": ["public/", "dept/", "projects/private-domain/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
    "virtual-ip": ["public/", "dept/", "projects/virtual-ip/", "entities/", "concepts/", "index.md", "overview.md", "log.md"],
}


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
    fm, body = extract_frontmatter(content)
    
    # 从 frontmatter 中提取
    lark_url = fm.get("lark_url", "")
    if lark_url:
        return lark_url
    
    # 从内容中提取
    match = re.search(r"https://[\w\-]+\.feishu\.cn/[\w/]+", content)
    if match:
        return match.group()
    return ""


def is_page_accessible(page_path: Path, scope: str | None = None) -> bool:
    """检查页面是否在指定 scope 的权限范围内"""
    if scope is None:
        return True

    allowed_prefixes = SCOPE_PATH_MAP.get(scope, SCOPE_PATH_MAP[None])
    rel_str = page_path.relative_to(WIKI_DIR).as_posix()

    for prefix in allowed_prefixes:
        if prefix == "" or rel_str.startswith(prefix) or rel_str == prefix.replace("/", ""):
            return True
    return False


def find_relevant_pages(question: str, scope: str | None = None) -> list[Path]:
    """通过关键词匹配 + 图邻居扩展找到相关页面（带权限过滤）"""
    index_content = read_file(INDEX_FILE)
    if not index_content:
        return []

    # 支持两种格式: [[wikilink]] 和 [title](href)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', index_content)
    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', index_content)
    
    all_links = []
    for title, href in md_links:
        all_links.append((title, href))
    for title in wiki_links:
        all_links.append((title, f"{title}.md"))
    
    question_lower = question.lower()
    if scope:
        question_lower = f"{question_lower} {scope.lower()}"

    relevant = []
    for title, href in all_links:
        title_lower = title.lower()
        has_cjk = any('一' <= ch <= '鿿' for ch in title)

        if has_cjk:
            matched = any(
                title_lower[j:j+2] in question_lower
                for j in range(len(title_lower) - 1)
                if any('一' <= c <= '鿿' for c in title_lower[j:j+2])
            )
        else:
            matched = any(word in question_lower for word in title_lower.split() if len(word) > 2)

        if scope and not matched:
            matched = scope.lower() in title_lower

        if matched:
            # 尝试在多个位置查找文件
            possible_paths = [
                WIKI_DIR / href,
                WIKI_DIR / "projects" / scope / "sources" / href,
                WIKI_DIR / "public" / "sources" / href,
                WIKI_DIR / "dept" / "sources" / href,
                WIKI_DIR / "entities" / href,
                WIKI_DIR / "concepts" / href,
            ]
            
            for p in possible_paths:
                if p.exists() and p not in relevant and is_page_accessible(p, scope):
                    relevant.append(p)
                    break

    # 图邻居扩展（受权限过滤）
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
                if np.exists() and np not in relevant and is_page_accessible(np, scope):
                    relevant.append(np)
        except (json.JSONDecodeError, KeyError):
            pass

    # 总是包含 overview（需权限检查）
    overview = WIKI_DIR / "overview.md"
    if overview.exists() and overview not in relevant and is_page_accessible(overview, scope):
        relevant.insert(0, overview)

    return relevant[:15]


def build_page_context(pages: list[Path]) -> str:
    """构建页面上下文，供 LLM 使用"""
    context_parts = []
    
    for p in pages:
        rel = p.relative_to(WIKI_DIR)
        content = read_file(p)
        fm, body = extract_frontmatter(content)
        
        title = fm.get("title", p.stem)
        if not title or title == p.stem:
            title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
        
        # 截断内容，避免过长
        preview = body[:2000] if len(body) > 2000 else body
        
        context_parts.append(f"""
---
文件: {rel}
标题: {title}
---
{preview}
""")
    
    return "\n".join(context_parts)


def build_sources_citation(pages: list[Path]) -> list[dict]:
    """构建来源引用信息列表，只输出有飞书链接的文档来源"""
    sources = []
    for p in pages:
        rel = p.relative_to(WIKI_DIR)
        content = read_file(p)
        fm, body = extract_frontmatter(content)

        title = fm.get("title", p.stem)
        if not title or title == p.stem:
            title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()

        # 获取飞书链接（优先 frontmatter，其次从内容提取）
        lark_url = fm.get("lark_url", "")
        if not lark_url:
            lark_url = extract_lark_url_from_page(p)
        
        # 只保留有飞书链接的来源
        if lark_url:
            sources.append({
                "title": title,
                "wiki_path": str(rel),
                "lark_url": lark_url,
                "source_url": lark_url,
                "preview": body[:200].replace('\n', ' ') + "...",
            })
    return sources


def personal_intro() -> str:
    """返回司南 qa-bot 的自然个人介绍"""
    return (
        "嗨，我是 **司南**（Compass），MCN 事业部的智能知识助手~ 🧭\n\n"
        "我可以帮你：\n"
        "- 📚 **查知识**：项目 SOP、流程规范、方法论...\n"
        "- 📊 **看数据**：周报指标、KPI、转化率...\n"
        "- 🔄 **刷新知识库**：同步最新飞书文档\n"
        "- 🕸️ **看图谱**：项目知识关联可视化\n\n"
        "直接 @我 或发送你的问题就好，比如：\n"
        "- \"达人筛选标准是什么\"\n"
        "- \"看看垂类达人孵化的本周数据\"\n"
        "- \"刷新一下知识库\"\n\n"
        "有问必答，知无不言~"
    )


def query_graph(open_browser: bool = True) -> dict:
    """查询知识图谱，返回图谱页面信息"""
    if not GRAPH_HTML.exists():
        return {
            "html_path": str(GRAPH_HTML),
            "opened": False,
            "error": "知识图谱尚未生成，请先执行 'build the knowledge graph'",
        }

    html_path = str(GRAPH_HTML.resolve())
    opened = False
    if open_browser:
        try:
            webbrowser.open(f"file://{html_path}")
            opened = True
        except Exception:
            pass

    return {
        "html_path": html_path,
        "opened": opened,
        "message": f"知识图谱已生成：file://{html_path}",
    }


def query_wiki(question: str, scope: str | None = None) -> dict:
    """查询 Compass 知识库（带权限隔离）
    
    返回检索结果，供 OpenClaw LLM 综合生成回答
    
    Args:
        question: 用户问题
        scope: 权限范围（如"kol-incubation"），用于过滤可访问页面
        
    Returns:
        dict: {
            "pages": [Path, ...],           # 相关页面路径列表
            "context": "...",               # 页面内容上下文（供 LLM 使用）
            "sources": [{"title": "...", "wiki_path": "...", "lark_url": "..."}],
            "scope": "..." | None,
            "total_pages": N,               # 找到的总页面数
            "has_permission_issue": False,   # 是否有权限问题
        }
    """
    # Step 1: 读取索引
    index_content = read_file(INDEX_FILE)
    if not index_content:
        return {
            "pages": [],
            "context": "知识库为空。请先使用 wiki_ingest.py 导入文档，或说\"刷新知识库\"。",
            "sources": [],
            "scope": scope,
            "total_pages": 0,
            "has_permission_issue": False,
        }

    # Step 2: 找到相关页面
    relevant_pages = find_relevant_pages(question, scope)

    # Step 3: 构建上下文
    context = build_page_context(relevant_pages)
    
    # Step 4: 构建来源引用
    sources = build_sources_citation(relevant_pages)

    return {
        "pages": relevant_pages,
        "context": context,
        "sources": sources,
        "scope": scope,
        "total_pages": len(relevant_pages),
        "has_permission_issue": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Query Compass wiki (retrieval only)")
    parser.add_argument("question", type=str, help="Question to ask")
    parser.add_argument("--scope", type=str, default=None, help="Scope filter")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = query_wiki(args.question, scope=args.scope)
    
    if args.json:
        # JSON 输出（不包含 Path 对象）
        json_result = {
            "context": result["context"],
            "sources": result["sources"],
            "scope": result["scope"],
            "total_pages": result["total_pages"],
            "has_permission_issue": result["has_permission_issue"],
        }
        print(json.dumps(json_result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print(f"找到 {result['total_pages']} 个相关页面")
        print("=" * 60)
        print("\n📚 Sources:")
        for source in result["sources"]:
            # 优先显示飞书网页链接
            if source.get('lark_url'):
                print(f"  • [{source['title']}]({source['lark_url']})")
            else:
                print(f"  • [[{source['title']}]] ({source['wiki_path']})")
        
        print("\n" + "=" * 60)
        print("页面内容上下文（供 LLM 使用）：")
        print("=" * 60)
        print(result["context"][:2000])  # 截断显示
        if len(result["context"]) > 2000:
            print(f"\n... (共 {len(result['context'])} 字符)")


if __name__ == "__main__":
    main()
