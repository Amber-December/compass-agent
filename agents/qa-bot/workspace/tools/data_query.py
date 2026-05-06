#!/usr/bin/env python3
"""
Compass QA-Bot Data Query — 结构化数据智能检索工具

功能：
- 根据用户问题，解析查询意图（达人、周次、日期、指标等）
- 从 workspace/knowledge/data/<scope>/ 下的 JSON 文件中精准检索记录
- 支持单条查询、跨周对比、聚合统计
- 返回结构化数据上下文，供 OpenClaw LLM 生成回答

数据格式说明：
  所有 JSON 均为飞书 Base 导出格式：
  {
    "ok": true,
    "data": {
      "fields": ["字段1", "字段2", ...],
      "data": [
        ["值1", "值2", ...],
        ...
      ]
    }
  }

Usage:
    python tools/data_query.py "K001 Week 2 粉丝数" --scope kol-incubation --json
    python tools/data_query.py "苏小棠 Week 1 和 Week 2 粉丝对比" --scope kol-incubation --json
    python tools/data_query.py "所有达人的周收入" --scope kol-incubation --json

API:
    from tools.data_query import query_data
    result = query_data("K001 Week 2 粉丝数", scope="kol-incubation")
    # result = {"records": [...], "context": "...", "sources": [...], "analysis": "..."}
"""

from __future__ import annotations
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

REPO_ROOT = _find_repo_root()
DATA_DIR = REPO_ROOT / "workspace" / "knowledge" / "data"

# 权限范围映射
SCOPE_PATH_MAP = {
    None: [""],
    "dept": [""],
    "kol-incubation": ["kol-incubation"],
    "brand-ops": ["brand-ops"],
    "live-commerce": ["live-commerce"],
    "short-video": ["short-video"],
    "private-domain": ["private-domain"],
    "virtual-ip": ["virtual-ip"],
}

# 指标别名映射（中文问题中的指标名称 -> JSON 字段名）
# 注意：为避免子串误匹配，过于宽泛的短别名已移除（如 "粉丝" → "粉丝数"）
METRIC_ALIASES = {
    "粉丝数": "粉丝数",
    "粉丝量": "粉丝数",
    "播放量": "总播放量",
    "总播放": "总播放量",
    "收入": "周收入",
    "周收入": "周收入",
    "完播率": "平均完播率",
    "平均完播率": "平均完播率",
    "粉丝增长率": "粉丝增长率",
    "涨粉率": "粉丝增长率",
    "内容数": "内容数",
    "作品数": "内容数",
    "爆款数": "爆款内容数",
    "爆款内容数": "爆款内容数",
    "商单数": "商单内容数",
    "商单内容数": "商单内容数",
    "商单转化率": "商单转化率",
    "等级": "等级",
    "达人类型": "达人类型",
    "类型": "达人类型",
    "昵称": "达人昵称",
    "达人昵称": "达人昵称",
    "姓名": "达人昵称",
    # 项目 KPI 字段（kol-incubation）
    "达人周均变现": "达人周均变现",
    "商单转化率": "商单转化率",
    "平均粉丝增长率": "平均粉丝增长率",
    "项目状态": "项目状态",
    "头部达人": "头部达人数量",
    "头部达人数量": "头部达人数量",
    "活跃达人": "活跃达人数量",
    "活跃达人数量": "活跃达人数量",
    "新增签约": "新增签约达人",
    "新增签约达人": "新增签约达人",
    "周总营收": "周总营收",
    # 项目 KPI 字段（live-commerce）
    "GMV": "总GMV",
    "总GMV": "总GMV",
    "直播转化率": "直播转化率",
    "ROI": "ROI",
    "总订单": "总订单数",
    "总订单数": "总订单数",
    "场均观看": "场均观看",
    "活跃主播": "活跃主播数",
    "活跃主播数": "活跃主播数",
    "总投流费用": "总投流费用",
    "投流费用": "总投流费用",
    # 内容产出字段
    "内容标题": "内容标题",
    "标题": "内容标题",
    "品牌": "品牌名称",
    "品牌名称": "品牌名称",
    "内容类型": "内容类型",
    "选题": "选题标签",
    "选题标签": "选题标签",
    "是否爆款": "是否爆款",
}

# 仅出现在项目周度KPI中的指标（用于自动推断 file_hint）
PROJECT_ONLY_METRICS = {
    "达人周均变现", "商单转化率", "平均粉丝增长率", "项目状态",
    "头部达人数量", "活跃达人数量", "新增签约达人", "周总营收",
    "总GMV", "ROI", "直播转化率", "总订单数", "场均观看",
    "活跃主播数", "总投流费用",
}

# 文件别名映射
FILE_ALIASES = {
    "达人周度快照": "达人周度快照",
    "周度快照": "达人周度快照",
    "达人": "达人周度快照",
    "达人档案": "达人档案",
    "档案": "达人档案",
    "内容产出": "内容产出",
    "内容": "内容产出",
    "品牌合作": "品牌合作",
    "合作": "品牌合作",
    "团队档案": "团队档案",
    "团队": "团队档案",
    "项目KPI": "项目周度KPI",
    "KPI": "项目周度KPI",
    "项目周度KPI": "项目周度KPI",
}


def is_data_accessible(project_dir: Path, scope: str | None = None) -> bool:
    if scope is None:
        return True
    allowed_prefixes = SCOPE_PATH_MAP.get(scope, [])
    project_name = project_dir.name
    for prefix in allowed_prefixes:
        if prefix == "" or project_name == prefix:
            return True
    return False


def find_data_files(scope: str | None = None) -> list[Path]:
    """查找可访问的数据文件"""
    if not DATA_DIR.exists():
        return []
    files = []
    for project_dir in DATA_DIR.iterdir():
        if project_dir.is_dir() and is_data_accessible(project_dir, scope):
            for data_file in sorted(project_dir.iterdir()):
                if data_file.suffix == '.json' and not data_file.name.endswith('_meta.json'):
                    files.append(data_file)
    return files


def parse_base_json(file_path: Path) -> list[dict]:
    """解析飞书 Base 导出的 JSON，返回字典列表（字段名作为 key）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    data_obj = raw.get("data", {})
    fields = data_obj.get("fields", [])
    rows = data_obj.get("data", [])

    records = []
    for row in rows:
        record = {}
        for i, field in enumerate(fields):
            if i < len(row):
                record[field] = row[i]
            else:
                record[field] = None
        records.append(record)
    return records


def extract_query_params(question: str) -> dict:
    """从问题中提取查询参数"""
    params = {
        "kol_id": None,       # 达人编号如 K001
        "kol_name": None,     # 达人昵称如 苏小棠
        "weeks": [],          # 周次列表 [1, 2]
        "date_range": None,   # 日期范围
        "metrics": [],        # 指标列表
        "file_hint": None,    # 文件类型提示
        "compare": False,     # 是否对比
        "all": False,         # 是否查所有
    }

    q = question.lower()

    # 提取达人编号（K001, K002...）
    kol_match = re.search(r'[Kk](\d{3})', question)
    if kol_match:
        params["kol_id"] = f"K{kol_match.group(1).zfill(3)}"

    # 提取周次
    week_matches = re.findall(r'[Ww]eek\s*(\d+)|第?\s*(\d+)\s*周|周\s*(\d+)', q)
    for m in week_matches:
        for g in m:
            if g:
                params["weeks"].append(int(g))
    params["weeks"] = sorted(list(set(params["weeks"])))

    # 提取日期范围（简化匹配）
    date_match = re.search(r'(\d{4}-\d{2}-\d{2}).*?(\d{4}-\d{2}-\d{2})', question)
    if date_match:
        params["date_range"] = (date_match.group(1), date_match.group(2))

    # 检测是否对比
    if any(kw in q for kw in ["对比", "比较", "vs", "增长", "下降", "变化", "差", "环比", "和"]):
        params["compare"] = True

    # 检测是否查所有
    if any(kw in q for kw in ["所有", "全部", "各达人", "每个", "汇总", "总计", "平均"]):
        params["all"] = True

    # 提取指标
    for alias, field_name in METRIC_ALIASES.items():
        if alias in question:
            if field_name not in params["metrics"]:
                params["metrics"].append(field_name)

    # 提取文件类型提示
    for alias, file_prefix in FILE_ALIASES.items():
        if alias in question:
            params["file_hint"] = file_prefix
            break

    # 尝试从问题中匹配达人昵称（2-4 个中文字符，排除常见指标/文件名词）
    EXCLUDED_NAMES = {"达人", "粉丝", "粉丝数", "周度", "快照", "内容", "品牌", "团队", "项目", "收入", "变现",
                      "完播率", "增长率", "涨粉率", "内容数", "作品数", "爆款", "商单", "等级",
                      "类型", "昵称", "姓名", "档案", "合作", "KPI", "播放", "指标", "所有达人", "所有",
                      "垂类", "孵化", "电商", "直播", "运营", "虚拟", "品牌代",
                      "垂类达人", "直播电商", "品牌代运", "品牌代运营", "私域运营", "私域",
                      "短视频", "内容矩阵", "虚拟IP", "IP孵化"}
    name_patterns = re.findall(r'[\u4e00-\u9fa5]{2,4}', question)
    for name in name_patterns:
        if name not in EXCLUDED_NAMES:
            params["kol_name"] = name
            break

    # 自动推断 file_hint：如果包含项目级指标，则定位到项目周度KPI
    if any(m in PROJECT_ONLY_METRICS for m in params["metrics"]):
        params["file_hint"] = "项目周度KPI"

    # 趋势/范围查询："从 Week X 到 Week Y" 或 "从第 X 周到第 Y 周" 不过滤具体周次
    if re.search(r'从\s*(?:Week\s*\d+|第?\s*\d+\s*周)\s*.*?到\s*(?:Week\s*\d+|第?\s*\d+\s*周)', question):
        params["weeks"] = []
        params["trend"] = True

    return params


def filter_records(records: list[dict], params: dict) -> list[dict]:
    """根据查询参数过滤记录"""
    filtered = records

    # 按达人编号过滤
    if params.get("kol_id"):
        filtered = [r for r in filtered if r.get("达人编号") == params["kol_id"]]

    # 按达人昵称过滤（"所有"模式下不过滤；记录中无达人昵称字段时也不过滤）
    if params.get("kol_name") and not params.get("kol_id") and not params.get("all"):
        if any("达人昵称" in r for r in filtered):
            filtered = [r for r in filtered if params["kol_name"] in str(r.get("达人昵称", ""))]

    # 按周次过滤
    if params.get("weeks"):
        filtered = [r for r in filtered if r.get("周次") in params["weeks"]]

    # 按日期范围过滤（仅当没有指定周次时作为辅助条件，避免冲突）
    if params.get("date_range") and not params.get("weeks"):
        start, end = params["date_range"]
        filtered = [r for r in filtered if start in str(r.get("日期范围", "")) or end in str(r.get("日期范围", ""))]

    return filtered


def format_record_table(records: list[dict], metrics: list[str] = None, max_rows: int = 20) -> str:
    """将记录格式化为 Markdown 表格"""
    if not records:
        return "（无匹配记录）"

    # 确定要展示的字段
    if metrics:
        # 始终包含的标识字段
        display_fields = []
        for f in ["达人编号", "达人昵称", "周次", "日期范围"]:
            if f in records[0] and f not in metrics:
                display_fields.append(f)
        for m in metrics:
            if m in records[0] and m not in display_fields:
                display_fields.append(m)
    else:
        display_fields = list(records[0].keys())

    lines = []
    lines.append("| " + " | ".join(display_fields) + " |")
    lines.append("| " + " | ".join(["---"] * len(display_fields)) + " |")

    for r in records[:max_rows]:
        row = []
        for f in display_fields:
            val = r.get(f, "")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            elif isinstance(val, float):
                val = f"{val:.4f}" if val < 0.1 else f"{val:.2f}"
            else:
                val = str(val) if val is not None else ""
            row.append(val)
        lines.append("| " + " | ".join(row) + " |")

    if len(records) > max_rows:
        lines.append(f"\n*（共 {len(records)} 条记录，展示前 {max_rows} 条）*")

    return "\n".join(lines)


def _fmt_num(val):
    """智能格式化数值：小数保留精度，大数取整"""
    if not isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, float):
        if 0 < abs(val) < 1:
            return f"{val:.4f}"
        if abs(val) < 100:
            return f"{val:.2f}"
    return f"{val:,.0f}"


def compute_analysis(records: list[dict], metrics: list[str], params: dict) -> str:
    """计算分析结果（如跨周对比、增长等）"""
    analysis_parts = []

    if not records:
        return ""

    # 单达人跨周对比 / 趋势查询
    is_trend = params.get("trend")
    if ((params.get("compare") and len(params.get("weeks", [])) >= 2) or is_trend) and len(metrics) > 0:
        kol_id = params.get("kol_id") or records[0].get("达人编号")
        kol_name = records[0].get("达人昵称", "")
        entity_name = kol_name or kol_id or "项目"

        for metric in metrics:
            if metric not in records[0]:
                continue

            # 按周次排序
            week_data = {}
            for r in records:
                if r.get("达人编号") == kol_id or not kol_id:
                    w = r.get("周次")
                    if w is not None:
                        week_data[w] = r.get(metric)

            if len(week_data) >= 2:
                weeks = sorted(week_data.keys())
                analysis_parts.append(f"\n**{entity_name} 的 {metric} 跨周变化：**")
                for i in range(1, len(weeks)):
                    prev_w, curr_w = weeks[i-1], weeks[i]
                    prev_v = week_data[prev_w]
                    curr_v = week_data[curr_w]
                    if isinstance(prev_v, (int, float)) and isinstance(curr_v, (int, float)) and prev_v != 0:
                        delta = curr_v - prev_v
                        pct = (delta / prev_v) * 100
                        analysis_parts.append(
                            f"- Week {prev_w} → Week {curr_w}: {_fmt_num(prev_v)} → {_fmt_num(curr_v)} "
                            f"(变化: {_fmt_num(delta)}, {pct:+.2f}%)"
                        )
                    elif isinstance(prev_v, (int, float)) and isinstance(curr_v, (int, float)):
                        analysis_parts.append(
                            f"- Week {prev_w} → Week {curr_w}: {_fmt_num(prev_v)} → {_fmt_num(curr_v)}"
                        )

    # 多达人聚合（查所有时）
    if params.get("all") and len(records) > 1:
        for metric in metrics:
            if metric not in records[0]:
                continue
            values = [r.get(metric) for r in records if isinstance(r.get(metric), (int, float))]
            if values:
                avg_val = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)
                analysis_parts.append(
                    f"\n**{metric} 聚合统计**："
                    f"平均 {_fmt_num(avg_val)}, 最高 {_fmt_num(max_val)}, 最低 {_fmt_num(min_val)}"
                )

    return "\n".join(analysis_parts)


def find_matching_files(data_files: list[Path], params: dict) -> list[Path]:
    """根据文件类型提示和记录内容，找到最匹配的数据文件"""
    if not params.get("file_hint"):
        # 没有文件提示时，返回所有文件
        return data_files

    hint = params["file_hint"]
    matched = [f for f in data_files if hint in f.name]
    if matched:
        return matched
    return data_files


def query_data(question: str, scope: str | None = None) -> dict:
    """智能查询数据

    Args:
        question: 用户问题（如 "K001 Week 2 粉丝数"）
        scope: 权限范围

    Returns:
        dict: {
            "records": [...],       # 匹配的记录列表（字典格式）
            "context": "...",       # 结构化数据上下文
            "analysis": "...",      # 分析结果（对比、聚合等）
            "sources": [...],       # 来源信息
            "params": {...},        # 解析出的查询参数
            "total_records": N,     # 匹配记录数
            "scope": "...",
        }
    """
    # 1. 解析查询参数
    params = extract_query_params(question)

    # 2. 查找数据文件
    data_files = find_data_files(scope)
    matching_files = find_matching_files(data_files, params)

    if not matching_files:
        return {
            "records": [],
            "context": "暂无数据。请先同步 Base 数据，或联系 wiki-manager 执行数据同步。",
            "analysis": "",
            "sources": [],
            "params": params,
            "total_records": 0,
            "scope": scope,
        }

    # 3. 读取并过滤数据
    all_records = []
    sources = []
    for file_path in matching_files:
        records = parse_base_json(file_path)
        if records:
            filtered = filter_records(records, params)
            all_records.extend(filtered)
            sources.append({
                "project": file_path.parent.name,
                "table": file_path.stem,
                "records_matched": len(filtered),
                "records_total": len(records),
            })

    # 4. 去重（基于快照编号或达人编号+周次）
    seen = set()
    deduped = []
    for r in all_records:
        key = r.get("快照编号") or f"{r.get('达人编号','')}_{r.get('周次','')}"
        if key and key not in seen:
            seen.add(key)
            deduped.append(r)
    all_records = deduped

    # 5. 过滤掉无匹配的来源，减少噪音
    sources = [s for s in sources if s["records_matched"] > 0]

    # 6. 生成上下文和分析
    if all_records:
        context = format_record_table(all_records, params["metrics"] or None)
        analysis = compute_analysis(all_records, params["metrics"] or [], params)
    else:
        context = "（未找到匹配的记录）"
        analysis = ""

    return {
        "records": all_records,
        "context": context,
        "analysis": analysis,
        "sources": sources,
        "params": params,
        "total_records": len(all_records),
        "scope": scope,
    }


def main():
    parser = argparse.ArgumentParser(description="Compass Data Query — 智能数据检索")
    parser.add_argument("question", type=str, help="查询问题")
    parser.add_argument("--scope", type=str, default=None, help="权限范围")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    result = query_data(args.question, scope=args.scope)

    if args.json:
        json_result = {
            "context": result["context"],
            "analysis": result["analysis"],
            "sources": result["sources"],
            "params": result["params"],
            "total_records": result["total_records"],
            "scope": result["scope"],
        }
        print(json.dumps(json_result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print(f"查询: {args.question}")
        print(f"解析参数: {json.dumps(result['params'], ensure_ascii=False)}")
        print(f"匹配记录: {result['total_records']} 条")
        print("=" * 60)
        print("\n📊 数据：")
        print(result["context"])
        if result["analysis"]:
            print("\n📈 分析：")
            print(result["analysis"])
        print("\n📁 来源：")
        for s in result["sources"]:
            print(f"  • {s['project']}/{s['table']} — {s['file']} (匹配 {s['records_matched']}/{s['records_total']} 条)")


if __name__ == "__main__":
    main()
