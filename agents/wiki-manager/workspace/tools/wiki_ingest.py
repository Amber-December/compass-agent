#!/usr/bin/env python3
"""
wiki_ingest.py - 知识编译执行脚本

职责：读取原始 Markdown，调用 LLM 处理，写入 wiki/ 目录。
所有业务规则（实体提取、概念过滤、归一化）由 LLM 按 SKILL.md 规范执行。
本脚本只负责：文件 IO、路径计算、增量判断、调用 LLM、写入输出。
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 配置
def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

REPO_ROOT = _find_repo_root()
AGENT_WORKSPACE = REPO_ROOT / "agents" / "wiki-manager" / "workspace"
RAW_LARK = AGENT_WORKSPACE / "raw_lark" / "wiki"
WIKI = REPO_ROOT / "workspace" / "knowledge" / "wiki"

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """解析 YAML frontmatter"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            try:
                import yaml
                frontmatter = yaml.safe_load(fm_text) or {}
                return frontmatter, body
            except ImportError:
                pass
            # Fallback: 简易行解析（无 PyYAML 时）
            frontmatter = {}
            current_key = None
            current_value = []
            for line in fm_text.split('\n'):
                if ':' in line and not line.startswith(' ') and not line.startswith('-'):
                    if current_key:
                        frontmatter[current_key] = '\n'.join(current_value).strip()
                    key, value = line.split(':', 1)
                    current_key = key.strip()
                    current_value = [value.strip()]
                else:
                    if current_key:
                        current_value.append(line)
            if current_key:
                frontmatter[current_key] = '\n'.join(current_value).strip()
            return frontmatter, body
    return {}, content

def generate_slug(title: str) -> str:
    """生成 kebab-case slug"""
    slug = re.sub(r'[^\u4e00-\u9fff\w\s\-\[\]]', '', title)
    slug = slug.strip().replace(' ', '-').replace('——', '-').replace('—', '-')
    slug = re.sub(r'-+', '-', slug)
    return slug.lower()

def get_output_path(frontmatter: Dict, slug: str) -> Path:
    """根据 scope 和 project_id 计算输出路径"""
    scope = frontmatter.get('scope', 'public')
    project_id = frontmatter.get('project_id', '')
    
    if scope == 'projects' and project_id:
        return WIKI / "projects" / project_id / "sources" / f"{slug}.md"
    else:
        return WIKI / scope / "sources" / f"{slug}.md"

def ingest_file(filepath: Path) -> Dict:
    """执行单篇文档的 ingest"""
    print(f"\n📄 Ingest: {filepath.name}")
    
    # Step 0: 读取并解析
    content = filepath.read_text(encoding='utf-8')
    frontmatter, body = parse_frontmatter(content)
    
    title = frontmatter.get('title', filepath.stem)
    scope = frontmatter.get('scope', 'public')
    project_id = frontmatter.get('project_id', '')
    content_hash = frontmatter.get('content_hash', '')
    status = frontmatter.get('status', 'active')
    lark_url = frontmatter.get('lark_url', '')
    doc_type = frontmatter.get('doc_type', '')

    if status == 'archived':
        print(f"  ⏭️ 已归档，跳过")
        return {'skipped': True}
    
    # Step 0: 增量判断
    slug = generate_slug(title)
    output_path = get_output_path(frontmatter, slug)
    
    if output_path.exists():
        existing = output_path.read_text(encoding='utf-8')
        existing_fm, _ = parse_frontmatter(existing)
        if existing_fm.get('content_hash') == content_hash:
            print(f"  ⏭️ Content unchanged, skipping")
            return {'skipped': True}
        else:
            print(f"  ↻ 内容变更，更新 (revision +1)")
    
    # Step 1-2: 读取上下文（由 LLM 在执行时读取）
    # Step 3: LLM 生成 Source Page（核心）
    # 这里只负责准备输入，实际 LLM 处理由调用方执行
    
    print(f"  📋 准备 LLM 处理: {scope}")
    if project_id:
        print(f"     项目: {project_id}")
    
    # 返回文档信息，供 LLM 处理
    return {
        'slug': slug,
        'scope': scope,
        'project_id': project_id,
        'title': title,
        'lark_url': lark_url,
        'content_hash': content_hash,
        'doc_type': doc_type,
        'frontmatter': frontmatter,
        'body': body,
        'output_path': str(output_path),
        'skipped': False
    }

def batch_ingest(dirpath: Path) -> List[Dict]:
    """批量 ingest 目录下的所有 .md 文件"""
    md_files = list(dirpath.rglob("*.md"))
    
    if not md_files:
        print(f"⚠️ 目录 {dirpath} 中没有 .md 文件")
        return []
    
    print(f"\n📁 批量 Ingest: {dirpath} ({len(md_files)} 个文件)")
    
    results = []
    for filepath in md_files:
        result = ingest_file(filepath)
        results.append(result)
    
    # 统计
    skipped = sum(1 for r in results if r.get('skipped'))
    to_process = [r for r in results if not r.get('skipped')]
    
    print(f"\n📊 统计:")
    print(f"   总计: {len(md_files)} 个文档")
    print(f"   跳过(未变更): {skipped} 个")
    print(f"   待 LLM 处理: {len(to_process)} 个")
    
    return to_process

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compass Wiki Ingest (执行脚本)')
    parser.add_argument('path', nargs='?', help='文件或目录路径')
    parser.add_argument('--batch', action='store_true', help='批量处理目录')
    parser.add_argument('--list', action='store_true', help='列出待处理文件（不执行）')
    
    args = parser.parse_args()
    
    if args.batch or (args.path and Path(args.path).is_dir()):
        path = Path(args.path) if args.path else RAW_LARK
        results = batch_ingest(path)
        
        if args.list:
            # 只列出，输出 JSON 供 LLM 读取
            print("\n📋 待处理文件列表:")
            for r in results:
                if not r.get('skipped'):
                    print(f"  - {r['title']} ({r['scope']})")
        else:
            # 输出 JSON 供 LLM 处理
            output = {
                'total': len(results),
                'files': [{
                    'slug': r['slug'],
                    'title': r['title'],
                    'scope': r['scope'],
                    'project_id': r['project_id'],
                    'doc_type': r.get('doc_type', ''),
                    'lark_url': r['lark_url'],
                    'content_hash': r['content_hash'],
                    'output_path': r['output_path'],
                    'frontmatter': r['frontmatter'],
                    'body_preview': r['body'][:500] + '...' if len(r['body']) > 500 else r['body']
                } for r in results if not r.get('skipped')]
            }
            print("\n" + json.dumps(output, ensure_ascii=False, indent=2))
    
    elif args.path:
        result = ingest_file(Path(args.path))
        if not result.get('skipped'):
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        # 默认处理 raw_lark/wiki/
        results = batch_ingest(RAW_LARK)
        output = {
            'total': len(results),
            'files': [{
                'slug': r['slug'],
                'title': r['title'],
                'scope': r['scope'],
                'project_id': r['project_id'],
                'doc_type': r.get('doc_type', ''),
                'lark_url': r['lark_url'],
                'content_hash': r['content_hash'],
                'output_path': r['output_path']
            } for r in results if not r.get('skipped')]
        }
        print("\n" + json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
