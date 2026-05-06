#!/usr/bin/env python3
"""
wiki_ingest_batch.py - 批量知识编译脚本（新规范）

职责：批量读取 raw_lark/wiki/ 下的 Markdown 文件，按 SKILL.md 新规范生成 Source Page。
核心原则：Additive Only（正文逐字保留，只 prepend 状态概览 + append 实体/概念引用）
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

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

def parse_frontmatter(content: str):
    """解析 YAML frontmatter，返回 (frontmatter_dict, body)"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
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

def get_output_path(frontmatter: dict, slug: str) -> Path:
    """根据 scope 和 project_id 计算输出路径"""
    scope = frontmatter.get('scope', 'public')
    project_id = frontmatter.get('project_id', '')
    
    if scope == 'projects' and project_id:
        return WIKI / "projects" / project_id / "sources" / f"{slug}.md"
    else:
        return WIKI / scope / "sources" / f"{slug}.md"

def extract_entities(body: str, project_id: str) -> list:
    """提取实体"""
    entities = []
    
    # 人员提取（2-4字中文人名）
    person_patterns = ['李小明', '张三', '李四', '王五', '赵六', '郑十三', '王小花', '陈九', '张十七', '钱二十一',
                       '林十', '黄十一', '吴十二', '吕十五', '施十六', '何十四', '孙七', '周八',
                       '王十九', '周二十三']
    for person in person_patterns:
        if person in body:
            # 判断角色
            role = "项目成员"
            if 'PM' in body and person in body:
                role = "PM"
            entities.append(f"- [[{person}]] — 类型: person | {role}")
    
    # KOL提取（K+数字）
    kol_matches = re.findall(r'K\d{3}', body)
    for kol in set(kol_matches):
        entities.append(f"- [[{kol}]] — 类型: kol | 签约达人")
    
    # 品牌提取
    brand_patterns = ['雅诗兰黛', '完美日记', '花西子', '欧莱雅', '兰蔻', '珀莱雅']
    for brand in brand_patterns:
        if brand in body:
            entities.append(f"- [[{brand}]] — 类型: brand | 合作品牌")
    
    # 项目提取（归一化）
    project_patterns = {
        '垂类达人孵化': '垂类达人孵化',
        '短视频内容矩阵': '短视频内容矩阵',
        '品牌代运营': '品牌代运营',
        '直播电商': '直播电商',
        '达人私域运营': '达人私域运营',
        '虚拟IP孵化': '虚拟IP孵化',
        '虚拟 IP 孵化': '虚拟IP孵化',
    }
    for pattern, standard in project_patterns.items():
        if pattern in body:
            entities.append(f"- [[{standard}]] — 类型: project | 在跑项目")
    
    # 平台提取
    platform_patterns = ['抖音', '小红书', 'B站', '快手', '淘宝直播', '微信视频号']
    for platform in platform_patterns:
        if platform in body:
            entities.append(f"- [[{platform}]] — 类型: platform | 内容平台")
    
    return list(set(entities))  # 去重

def extract_concepts(body: str) -> list:
    """提取概念"""
    concepts = []
    
    # SOP 相关
    sop_patterns = {
        '达人筛选': '达人筛选SOP',
        '内容策划': '内容策划SOP',
        '品牌合作': '品牌合作SOP',
        '整改经验': '整改经验SOP',
        '私域运营': '私域运营SOP',
        '直播运营': '直播运营SOP',
        'IP孵化': 'IP孵化SOP',
    }
    for pattern, concept in sop_patterns.items():
        if pattern in body and 'SOP' in body:
            concepts.append(f"- [[{concept}]] — 类型: SOP | 标准流程")
    
    # 指标相关
    metric_patterns = {
        '粉丝增长率': '粉丝增长率',
        '商单转化率': '商单转化率',
        'GMV': 'GMV',
        'ROI': 'ROI',
        '完播率': '完播率',
        '爆款率': '爆款率',
        '转化率': '转化率',
    }
    for pattern, concept in metric_patterns.items():
        if pattern in body:
            concepts.append(f"- [[{concept}]] — 类型: metric | 核心KPI")
    
    # 策略相关
    strategy_patterns = {
        '跨平台': '跨平台运营',
        '内容差异化': '内容差异化',
        '流量投放': '流量投放策略',
        '会员体系': '会员体系',
    }
    for pattern, concept in strategy_patterns.items():
        if pattern in body:
            concepts.append(f"- [[{concept}]] — 类型: strategy | 运营策略")
    
    # 工具相关
    tool_patterns = {
        'Notion AI': 'Notion AI',
        'AI剪辑': 'AI剪辑',
        '千川': '千川',
        'DOU+': 'DOU+',
        '动捕设备': '动捕设备',
    }
    for pattern, concept in tool_patterns.items():
        if pattern in body:
            concepts.append(f"- [[{concept}]] — 类型: tool | 技术工具")
    
    return list(set(concepts))  # 去重

def extract_concepts(body: str) -> list:
    """提取概念"""
    concepts = []
    
    # SOP 相关
    sop_patterns = {
        '达人筛选': '达人筛选SOP',
        '内容策划': '内容策划SOP',
        '品牌合作': '品牌合作SOP',
        '整改经验': '整改经验SOP',
        '私域运营': '私域运营SOP',
        '直播运营': '直播运营SOP',
        'IP孵化': 'IP孵化SOP',
    }
    for pattern, concept in sop_patterns.items():
        if pattern in body and 'SOP' in body:
            concepts.append(f"- [[{concept}]] — 类型: SOP | 标准流程")
    
    # 指标相关
    metric_patterns = {
        '粉丝增长率': '粉丝增长率',
        '商单转化率': '商单转化率',
        'GMV': 'GMV',
        'ROI': 'ROI',
        '完播率': '完播率',
        '爆款率': '爆款率',
        '转化率': '转化率',
    }
    for pattern, concept in metric_patterns.items():
        if pattern in body:
            concepts.append(f"- [[{concept}]] — 类型: metric | 核心KPI")
    
    # 策略相关
    strategy_patterns = {
        '跨平台': '跨平台运营',
        '内容差异化': '内容差异化',
        '流量投放': '流量投放策略',
        '会员体系': '会员体系',
    }
    for pattern, concept in strategy_patterns.items():
        if pattern in body:
            concepts.append(f"- [[{concept}]] — 类型: strategy | 运营策略")
    
    # 工具相关
    tool_patterns = {
        'Notion AI': 'Notion AI',
        'AI剪辑': 'AI剪辑',
        '千川': '千川',
        'DOU+': 'DOU+',
        '动捕设备': '动捕设备',
    }
    for pattern, concept in tool_patterns.items():
        if pattern in body:
            concepts.append(f"- [[{concept}]] — 类型: tool | 技术工具")
    
    return list(set(concepts))  # 去重

def generate_source_page(filepath: Path) -> dict:
    """生成 Source Page（新规范：Additive Only）"""
    content = filepath.read_text(encoding='utf-8')
    frontmatter, body = parse_frontmatter(content)
    
    title = frontmatter.get('title', filepath.stem)
    doc_type = frontmatter.get('doc_type', 'default')
    scope = frontmatter.get('scope', 'public')
    project_id = frontmatter.get('project_id', '')
    lark_url = frontmatter.get('lark_url', '')
    lark_node_id = frontmatter.get('lark_node_id', '')
    content_hash = frontmatter.get('content_hash', '')
    status = frontmatter.get('status', 'active')
    
    slug = generate_slug(title)
    output_path = get_output_path(frontmatter, slug)
    
    # 提取实体和概念
    entities = extract_entities(body, project_id)
    concepts = extract_concepts(body)
    
    # 生成相对路径
    try:
        rel_path = filepath.relative_to(RAW_LARK)
        source_file = f"raw_lark/wiki/{rel_path}"
    except ValueError:
        source_file = str(filepath)
    
    # 构建 frontmatter（新规范：来源元数据 + wiki 运行时）
    fm_lines = [
        "---",
        "# 来源元数据（透传）",
        f'title: "{title}"',
        f'doc_type: {doc_type}',
        f'scope: "{scope}"',
    ]
    
    if project_id:
        fm_lines.append(f'project_id: "{project_id}"')
    
    fm_lines.extend([
        f'lark_url: "{lark_url}"',
        f'lark_node_id: "{lark_node_id}"',
        f'content_hash: "{content_hash}"',
        f'status: {status}',
        "# wiki 运行时（ingest 生成）",
        "type: source",
        f'tags: [{doc_type}]',
        f"date: {datetime.now().strftime('%Y-%m-%d')}",
        f'source_file: "{source_file}"',
        "revision: 1",
        f"last_synced_at: {datetime.now().isoformat()}",
        "sources: []",
        "---",
    ])
    
    # 构建完整内容（Additive Only）
    parts = [
        "\n".join(fm_lines),
    ]
    
    # 正文（逐字保留）
    parts.append("## [以下正文逐字保留 raw_lark 原文，不得修改]\n")
    parts.append(body)
    parts.append("## [以上正文逐字保留 raw_lark 原文，不得修改]\n")
    
    # Append 实体引用
    if entities:
        parts.append("## 实体引用")
        parts.extend(entities)
        parts.append("")
    
    # Append 概念引用
    if concepts:
        parts.append("## 概念引用")
        parts.extend(concepts)
        parts.append("")
    
    # Append Contradictions
    parts.append("## Contradictions")
    parts.append("- 无\n")
    
    source_page = "\n".join(parts)
    
    return {
        'slug': slug,
        'output_path': output_path,
        'content': source_page,
        'doc_type': doc_type
    }

def batch_process(dirpath: Path):
    """批量处理目录下的所有 .md 文件"""
    md_files = list(dirpath.rglob("*.md"))
    
    if not md_files:
        print(f"⚠️ 目录 {dirpath} 中没有 .md 文件")
        return
    
    print(f"\n📁 批量 Ingest: {dirpath} ({len(md_files)} 个文件)")
    
    processed = 0
    skipped = 0
    errors = 0
    
    for filepath in md_files:
        try:
            result = generate_source_page(filepath)
            output_path = result['output_path']
            
            # 检查是否已存在（增量判断）
            if output_path.exists():
                existing = output_path.read_text(encoding='utf-8')
                existing_fm, _ = parse_frontmatter(existing)
                if existing_fm.get('content_hash') == result['content'].split('---')[1].split('content_hash:')[1].split('\n')[0].strip().strip('"'):
                    skipped += 1
                    continue
            
            # 确保目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入 Source Page
            output_path.write_text(result['content'], encoding='utf-8')
            processed += 1
            
            if processed % 10 == 0:
                print(f"  ✓ 已处理 {processed} 个文档...")
            
        except Exception as e:
            errors += 1
            print(f"  ✗ 错误处理 {filepath.name}: {e}")
    
    print(f"\n📊 批量处理完成:")
    print(f"   总计: {len(md_files)} 个文档")
    print(f"   新增/更新: {processed} 个")
    print(f"   跳过(未变更): {skipped} 个")
    print(f"   错误: {errors} 个")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compass Wiki Ingest (批量处理 - 新规范)')
    parser.add_argument('path', nargs='?', help='文件或目录路径')
    
    args = parser.parse_args()
    
    if args.path:
        path = Path(args.path)
        if path.is_dir():
            batch_process(path)
        else:
            result = generate_source_page(path)
            print(result['content'])
    else:
        batch_process(RAW_LARK)

if __name__ == '__main__':
    main()
