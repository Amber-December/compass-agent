#!/usr/bin/env python3
"""
生成垂类达人孵化项目的完整文档集（OnePage + 9周周报 + 9份会议纪要 + 项目文档）

用法:
    python scripts/generate_kol_project_docs.py
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path("/Users/amber/compass-agent/docs/projects/垂类达人孵化")

# 项目数据
PROJECT = {
    "name": "垂类达人孵化",
    "pm": "李小明",
    "members": "张三（内容）、李四（运营）、王五（商务）",
    "start": "2026-03-02",
    "status": "🟡 预警",
}

# 9 周数据
WEEKS = [
    {"week": 1, "date_range": "2026-03-02 至 2026-03-08", "new_kol": 2, "top_kol": 1, "growth": 0.15, "conversion": 0.10, "revenue": 1.5, "status": "🟢", "highlights": "项目启动，首批达人签约", "risks": "无", "plans": "继续招募素人，完善筛选流程"},
    {"week": 2, "date_range": "2026-03-09 至 2026-03-15", "new_kol": 1, "top_kol": 2, "growth": 0.18, "conversion": 0.12, "revenue": 1.8, "status": "🟢", "highlights": "头部达人粉丝破10万", "risks": "无", "plans": "启动内容培训，优化视频质量"},
    {"week": 3, "date_range": "2026-03-16 至 2026-03-22", "new_kol": 2, "top_kol": 3, "growth": 0.20, "conversion": 0.14, "revenue": 2.1, "status": "🟢", "highlights": "首个商单落地，转化率提升", "risks": "无", "plans": "拓展品牌合作渠道"},
    {"week": 4, "date_range": "2026-03-23 至 2026-03-29", "new_kol": 1, "top_kol": 4, "growth": 0.16, "conversion": 0.15, "revenue": 2.3, "status": "🟢", "highlights": "4名达人进入头部梯队", "risks": "内容同质化苗头", "plans": "差异化定位，避免内卷"},
    {"week": 5, "date_range": "2026-03-30 至 2026-04-05", "new_kol": 1, "top_kol": 5, "growth": 0.14, "conversion": 0.16, "revenue": 2.5, "status": "🟢", "highlights": "商单转化率达标（16%）", "risks": "粉丝增速放缓", "plans": "加强短视频内容创新"},
    {"week": 6, "date_range": "2026-04-06 至 2026-04-12", "new_kol": 1, "top_kol": 5, "growth": 0.10, "conversion": 0.17, "revenue": 2.6, "status": "🟡", "highlights": "商单转化率持续提升", "risks": "粉丝增长率下滑至10%", "plans": "分析内容数据，调整选题方向"},
    {"week": 7, "date_range": "2026-04-13 至 2026-04-19", "new_kol": 1, "top_kol": 6, "growth": 0.07, "conversion": 0.18, "revenue": 2.7, "status": "🟡", "highlights": "第6名头部达人诞生", "risks": "粉丝增长率继续下滑至7%", "plans": "启动整改方案，优化内容策略"},
    {"week": 8, "date_range": "2026-04-20 至 2026-04-26", "new_kol": 0, "top_kol": 6, "growth": 0.04, "conversion": 0.17, "revenue": 2.7, "status": "🔴", "highlights": "商单合作稳定", "risks": "粉丝增长率跌破5%阈值，连续2周低于5%", "plans": "召开数据下滑分析会，制定整改方案"},
    {"week": 9, "date_range": "2026-04-27 至 2026-05-03", "new_kol": 1, "top_kol": 6, "growth": 0.03, "conversion": 0.18, "revenue": 2.8, "status": "🔴", "highlights": "整改方案启动，新增签约1名潜力达人", "risks": "粉丝增长率连续3周低于5%，需重点关注", "plans": "执行整改方案：内容创新+流量投放+跨平台运营"},
]

# 会议纪要数据
MEETINGS = [
    {"date": "2026-03-03", "title": "项目启动会", "type": "项目启动", "participants": "李小明、张三、李四、王五、部门负责人赵总", "recorder": "李四", "agenda": ["项目目标对齐", "团队分工确认", "首月计划制定"], "key_points": [{"topic": "项目目标", "content": "本季度孵化8名头部达人，粉丝增长率保持12%以上，商单转化率15%", "conclusion": "目标确认，全员达成一致"}, {"topic": "团队分工", "content": "张三负责内容策划与制作，李四负责达人运营与数据监测，王五负责商务合作", "conclusion": "分工明确，各负其责"}], "decisions": ["确定首批招募10名素人达人", "建立周会机制，每周五复盘", "设立数据监测日报制度"], "todos": [{"item": "完成素人招募渠道梳理", "owner": "王五", "deadline": "2026-03-06", "priority": "🔴 高"}, {"item": "制定达人筛选评分表", "owner": "张三", "deadline": "2026-03-05", "priority": "🔴 高"}, {"item": "搭建数据监测看板", "owner": "李四", "deadline": "2026-03-07", "priority": "🟡 中"}], "risks": "时间紧任务重，需确保首月顺利启动", "next_meeting": "2026-03-10 达人筛选标准讨论会"},
    {"date": "2026-03-10", "title": "达人筛选标准讨论会", "type": "标准制定", "participants": "李小明、张三、李四、王五", "recorder": "张三", "agenda": ["现有筛选流程复盘", "筛选维度讨论", "评分表确认"], "key_points": [{"topic": "筛选维度", "content": "基础素质（形象、表达）40%、内容潜力（创意、专业度）35%、商业潜力（配合度、粉丝画像）25%", "conclusion": "三维度评分模型确定"}, {"topic": "试用期", "content": "建议设置2周试用期，试用期内无保底，按产出结算", "conclusion": "试用期制度确定，2周为观察期"}], "decisions": ["采用三维度评分模型", "设置2周试用期", "建立达人档案模板"], "todos": [{"item": "完成达人筛选评分表 V1.0", "owner": "张三", "deadline": "2026-03-12", "priority": "🔴 高"}, {"item": "发布招募信息到各平台", "owner": "王五", "deadline": "2026-03-11", "priority": "🔴 高"}, {"item": "设计达人档案模板", "owner": "李四", "deadline": "2026-03-13", "priority": "🟡 中"}], "risks": "筛选标准过严可能导致招募困难", "next_meeting": "2026-03-17 Week 2 复盘会"},
    {"date": "2026-03-17", "title": "Week 2 复盘会", "type": "周复盘", "participants": "李小明、张三、李四、王五", "recorder": "李四", "agenda": ["Week 2 数据回顾", "内容表现分析", "下周计划调整"], "key_points": [{"topic": "数据表现", "content": "新增签约1名达人，头部达人数量达2名，粉丝增长率18%（超预期）", "conclusion": "首月进展顺利，粉丝增长超预期"}, {"topic": "内容方向", "content": "美妆赛道内容反响最好，穿搭类次之，美食类需调整", "conclusion": "加大美妆赛道投入，美食类暂停招募"}], "decisions": ["重点布局美妆赛道", "美食类达人暂停新增", "头部达人启动商单对接"], "todos": [{"item": "对接首批商单资源", "owner": "王五", "deadline": "2026-03-20", "priority": "🔴 高"}, {"item": "制作美妆内容SOP", "owner": "张三", "deadline": "2026-03-22", "priority": "🔴 高"}, {"item": "分析竞品美食账号失败原因", "owner": "李四", "deadline": "2026-03-24", "priority": "🟢 低"}], "risks": "无重大风险", "next_meeting": "2026-03-24 内容方向调整会"},
    {"date": "2026-03-24", "title": "内容方向调整会", "type": "策略调整", "participants": "李小明、张三、李四、王五", "recorder": "张三", "agenda": ["各赛道数据对比", "内容同质化问题", "差异化策略讨论"], "key_points": [{"topic": "同质化问题", "content": "多名达人内容风格趋同，粉丝反馈'看腻了'", "conclusion": "必须做差异化定位，避免内部竞争"}, {"topic": "差异化方案", "content": "按细分领域划分：护肤教程、彩妆测评、成分科普、场景妆容", "conclusion": "4个细分领域各配1-2名达人"}], "decisions": ["4个美妆细分领域并行", "每位达人必须有自己的标签和人设", "建立内容排期表避免撞题"], "todos": [{"item": "重新分配达人细分领域", "owner": "李小明", "deadline": "2026-03-26", "priority": "🔴 高"}, {"item": "制作差异化人设方案", "owner": "张三", "deadline": "2026-03-28", "priority": "🔴 高"}, {"item": "建立内容排期共享表", "owner": "李四", "deadline": "2026-03-27", "priority": "🟡 中"}], "risks": "调整期可能出现短期数据波动", "next_meeting": "2026-03-31 月度复盘会"},
    {"date": "2026-03-31", "title": "月度复盘会（3月）", "type": "月度复盘", "participants": "李小明、张三、李四、王五、部门负责人赵总", "recorder": "李四", "agenda": ["3月整体数据回顾", "达成情况评估", "4月计划制定"], "key_points": [{"topic": "月度成绩", "content": "4名头部达人，粉丝增长率16%，商单转化率15%，首月达成率80%", "conclusion": "整体达标，粉丝增长和商单转化符合预期"}, {"topic": "4月目标", "content": "新增4名头部达人，粉丝增长率维持12%以上，商单转化率提升至16%", "conclusion": "目标合理，重点在内容创新和商业变现"}], "decisions": ["4月新增4名头部达人目标", "启动品牌合作谈判", "建立达人分级体系（S/A/B）"], "todos": [{"item": "完成3月复盘报告", "owner": "李四", "deadline": "2026-04-02", "priority": "🔴 高"}, {"item": "梳理品牌合作线索", "owner": "王五", "deadline": "2026-04-05", "priority": "🔴 高"}, {"item": "设计达人分级方案", "owner": "李小明", "deadline": "2026-04-03", "priority": "🟡 中"}], "risks": "4月竞争加剧，需关注竞品动态", "next_meeting": "2026-04-07 品牌合作洽谈会"},
    {"date": "2026-04-07", "title": "品牌合作洽谈会", "type": "商务会议", "participants": "李小明、王五、品牌方代表（雅诗兰黛、完美日记）", "recorder": "王五", "agenda": ["品牌需求沟通", "达人匹配方案", "合作模式讨论"], "key_points": [{"topic": "合作需求", "content": "雅诗兰黛希望合作2名头部达人做新品首发，完美日记需要3名达人做系列测评", "conclusion": "两个品牌均有明确合作意向"}, {"topic": "报价策略", "content": "头部达人单条视频报价8000-15000，系列合作可打包优惠", "conclusion": "采用阶梯报价，量大从优"}], "decisions": ["与雅诗兰黛签订2名达人合作协议", "与完美日记签订3名达人系列测评", "制定标准化商务报价单"], "todos": [{"item": "完成雅诗兰黛合作合同", "owner": "王五", "deadline": "2026-04-10", "priority": "🔴 高"}, {"item": "完成完美日记合作合同", "owner": "王五", "deadline": "2026-04-12", "priority": "🔴 高"}, {"item": "制作标准化商务报价单", "owner": "王五", "deadline": "2026-04-15", "priority": "🟡 中"}], "risks": "品牌方要求较急，需确保内容质量", "next_meeting": "2026-04-14 数据下滑分析会"},
    {"date": "2026-04-14", "title": "数据下滑分析会", "type": "问题分析", "participants": "李小明、张三、李四、王五", "recorder": "李四", "agenda": ["粉丝增长率下滑原因分析", "内容数据拆解", "竞品对比"], "key_points": [{"topic": "下滑原因", "content": "粉丝增长率从14%跌至7%，主要原因是内容同质化严重、平台算法调整、竞品加大投入", "conclusion": "三重因素叠加导致数据下滑"}, {"topic": "内容问题", "content": "近两周爆款率下降，完播率降低，用户评论'内容重复'增多", "conclusion": "内容创新不足是核心问题"}], "decisions": ["立即启动内容整改方案", "增加跨平台运营（抖音+小红书+B站）", "引入AI脚本工具提升创意产出"], "todos": [{"item": "制定内容整改详细方案", "owner": "张三", "deadline": "2026-04-17", "priority": "🔴 高"}, {"item": "调研竞品近期爆款内容", "owner": "李四", "deadline": "2026-04-16", "priority": "🔴 高"}, {"item": "测试AI脚本生成工具", "owner": "张三", "deadline": "2026-04-18", "priority": "🟡 中"}], "risks": "整改期可能出现短期数据进一步下滑", "next_meeting": "2026-04-21 整改方案评审会"},
    {"date": "2026-04-21", "title": "整改方案评审会", "type": "方案评审", "participants": "李小明、张三、李四、王五、部门负责人赵总", "recorder": "张三", "agenda": ["整改方案汇报", "资源需求确认", "执行计划敲定"], "key_points": [{"topic": "整改方案", "content": "3大举措：①内容创新（引入AI脚本+热点追踪）②跨平台运营（抖音+小红书+B站同步）③流量投放（DOU+和小红书薯条）", "conclusion": "方案全面，资源需求明确"}, {"topic": "预算", "content": "整改期需增加流量投放预算5万/月，AI工具费用3000/月", "conclusion": "预算申请通过，立即执行"}], "decisions": ["整改方案通过，立即执行", "增加月度预算5.3万", "设立周度数据追踪机制", "2周后评估整改效果"], "todos": [{"item": "购买AI脚本工具并培训团队", "owner": "张三", "deadline": "2026-04-24", "priority": "🔴 高"}, {"item": "开通跨平台账号并搭建运营流程", "owner": "李四", "deadline": "2026-04-25", "priority": "🔴 高"}, {"item": "启动首批流量投放测试", "owner": "李四", "deadline": "2026-04-23", "priority": "🔴 高"}, {"item": "设计周度数据追踪表", "owner": "李四", "deadline": "2026-04-22", "priority": "🟡 中"}], "risks": "整改效果需2-3周才能显现，短期压力较大", "next_meeting": "2026-04-28 月度总结会"},
    {"date": "2026-04-28", "title": "月度总结会（4月）", "type": "月度总结", "participants": "李小明、张三、李四、王五、部门负责人赵总", "recorder": "李四", "agenda": ["4月整体数据回顾", "整改首周效果评估", "5月计划制定"], "key_points": [{"topic": "月度成绩", "content": "6名头部达人，商单转化率18%（超预期），但粉丝增长率3%（严重低于目标）", "conclusion": "商业变现能力强，但粉丝增长遇瓶颈"}, {"topic": "整改首周", "content": "AI脚本工具已启用，跨平台账号已开通，流量投放测试中", "conclusion": "整改措施已落地，效果待观察"}], "decisions": ["5月核心目标：粉丝增长率回升至8%以上", "继续执行整改方案，加大流量投放", "启动素人面试×5，补充新鲜血液", "建立每日数据监测机制"], "todos": [{"item": "完成4月复盘报告", "owner": "李四", "deadline": "2026-04-30", "priority": "🔴 高"}, {"item": "安排5名素人面试", "owner": "王五", "deadline": "2026-05-05", "priority": "🔴 高"}, {"item": "优化流量投放策略", "owner": "李四", "deadline": "2026-05-03", "priority": "🔴 高"}, {"item": "制作每日数据监测看板", "owner": "李四", "deadline": "2026-04-30", "priority": "🟡 中"}], "risks": "粉丝增长回升需要时间，需保持耐心", "next_meeting": "2026-05-05 Week 10 复盘会"},
]


def generate_onepage():
    """生成项目 OnePage"""
    lines = [
        "# 垂类达人孵化 — 项目 OnePage",
        "",
        "## 基本信息",
        f"- **项目名称**：{PROJECT['name']}",
        f"- **项目目标**：头部达人 ≥8 名，月均粉丝增长 ≥12%，商单转化率 ≥15%，达人月均变现 ≥3万",
        f"- **项目负责人**：{PROJECT['pm']}",
        f"- **项目成员**：{PROJECT['members']}",
        f"- **启动时间**：{PROJECT['start']}",
        f"- **当前状态**：{PROJECT['status']}",
        "",
        "## 核心 KPI",
        "",
        "| 指标 | 目标值 | Week 9 当前值 | 状态 |",
        "|------|--------|---------------|------|",
        f"| 头部达人数量 | ≥8 名 | {WEEKS[-1]['top_kol']} 名 | {'🟢' if WEEKS[-1]['top_kol'] >= 8 else '🟡'} |",
        f"| 月均粉丝增长率 | ≥12% | {WEEKS[-1]['growth']*100:.0f}% | {'🟢' if WEEKS[-1]['growth'] >= 0.12 else '🔴'} |",
        f"| 商单转化率 | ≥15% | {WEEKS[-1]['conversion']*100:.0f}% | {'🟢' if WEEKS[-1]['conversion'] >= 0.15 else '🟡'} |",
        f"| 达人月均变现 | ≥3万 | {WEEKS[-1]['revenue']:.1f}万 | {'🟢' if WEEKS[-1]['revenue'] >= 3 else '🟡'} |",
        "",
        "## 本周进展（Week 9）",
        f"- **已完成**：{WEEKS[-1]['highlights']}",
        f"- **进行中**：整改方案执行中，流量投放测试中",
        f"- **阻塞/风险**：{WEEKS[-1]['risks']}",
        "",
        "## 历史趋势",
        "",
        "| 周次 | 头部达人 | 粉丝增长率 | 商单转化率 | 月均变现 |",
        "|------|----------|------------|------------|----------|",
    ]
    for w in WEEKS:
        lines.append(f"| Week {w['week']} | {w['top_kol']} | {w['growth']*100:.0f}% | {w['conversion']*100:.0f}% | {w['revenue']:.1f}万 |")
    lines.extend([
        "",
        "## 资源需求",
        "- **预算**：月度流量投放预算 5万，AI工具费用 3000/月",
        "- **人力**：内容策划 1人、达人运营 1人、商务 1人",
        "- **外部合作**：雅诗兰黛、完美日记等品牌合作推进中",
        "",
        "## 相关链接",
        "- [周报归档](./周报归档)",
        "- [会议纪要](./会议纪要)",
        "- [项目文档](./项目文档)",
        "- [数据看板](./数据看板)",
    ])
    return "\n".join(lines)


def generate_weekly_report(week_data):
    """生成周报"""
    prev = WEEKS[week_data["week"] - 2] if week_data["week"] > 1 else None
    lines = [
        f"# [{PROJECT['name']}] 周报 {week_data['date_range']}",
        "",
        "## 1. 本周数据看板",
        "",
        "| 指标 | 本周 | 上周 | 环比 | 目标 | 状态 |",
        "|------|------|------|------|------|------|",
    ]
    if prev:
        growth_change = f"{((week_data['growth'] - prev['growth']) / prev['growth'] * 100):+.0f}%"
        conv_change = f"{((week_data['conversion'] - prev['conversion']) / prev['conversion'] * 100):+.0f}%"
        rev_change = f"{((week_data['revenue'] - prev['revenue']) / prev['revenue'] * 100):+.0f}%"
    else:
        growth_change = "-"
        conv_change = "-"
        rev_change = "-"

    prev_new_kol = prev['new_kol'] if prev else 0
    prev_top_kol = prev['top_kol'] if prev else 0
    prev_growth_str = f"{prev['growth']*100:.0f}%" if prev else '-'
    prev_conv_str = f"{prev['conversion']*100:.0f}%" if prev else '-'
    prev_rev_str = f"{prev['revenue']:.1f}万" if prev else '-'
    lines.append(f"| 新增签约达人 | {week_data['new_kol']} | {prev['new_kol'] if prev else '-'} | {'+' if week_data['new_kol'] > prev_new_kol else ''}{week_data['new_kol'] - prev_new_kol} | - | {'🟢' if week_data['new_kol'] > 0 else '🟡'} |")
    lines.append(f"| 头部达人数量 | {week_data['top_kol']} | {prev['top_kol'] if prev else '-'} | +{week_data['top_kol'] - prev_top_kol} | ≥8 | {'🟢' if week_data['top_kol'] >= 8 else '🟡'} |")
    lines.append(f"| 平均粉丝增长率 | {week_data['growth']*100:.0f}% | {prev_growth_str} | {growth_change} | ≥12% | {'🟢' if week_data['growth'] >= 0.12 else '🔴' if week_data['growth'] < 0.05 else '🟡'} |")
    lines.append(f"| 商单转化率 | {week_data['conversion']*100:.0f}% | {prev_conv_str} | {conv_change} | ≥15% | {'🟢' if week_data['conversion'] >= 0.15 else '🟡'} |")
    lines.append(f"| 达人月均变现 | {week_data['revenue']:.1f}万 | {prev_rev_str} | {rev_change} | ≥3万 | {'🟢' if week_data['revenue'] >= 3 else '🟡'} |")
    lines.extend([
        "",
        "## 2. 任务完成情况",
        "- ✅ 已完成：" + week_data['highlights'],
        "- ⏳ 进行中：" + ("整改方案执行" if week_data['week'] >= 8 else "常规运营推进"),
        "- ❌ 延期：" + ("粉丝增长目标" if week_data['growth'] < 0.12 else "无"),
        "",
        "## 3. 风险与阻塞",
        f"- ⚠️ {week_data['risks']}",
        "",
        "## 4. 下周计划",
        f"- {week_data['plans']}",
        "",
        "## 5. 需要支持",
        "- 部门层面的资源协调（如需）",
    ])
    return "\n".join(lines)


def generate_meeting_note(meeting):
    """生成会议纪要"""
    lines = [
        f"# 会议纪要：{meeting['title']}",
        "",
        "## 基本信息",
        f"- **会议主题**：{meeting['title']}",
        f"- **会议时间**：{meeting['date']}",
        f"- **会议地点**：线上飞书会议",
        f"- **参会人员**：{meeting['participants']}",
        f"- **记录人**：{meeting['recorder']}",
        f"- **会议类型**：{meeting['type']}",
        "",
        "---",
        "",
        "## 会议议程",
    ]
    for i, item in enumerate(meeting['agenda'], 1):
        lines.append(f"{i}. {item}")
    lines.extend([
        "",
        "---",
        "",
        "## 讨论要点",
        "",
    ])
    for point in meeting['key_points']:
        lines.extend([
            f"### 议题：{point['topic']}",
            f"- **背景**：{point['content']}",
            f"- **关键结论**：{point['conclusion']}",
            "",
        ])
    lines.extend([
        "---",
        "",
        "## 决策与结论",
    ])
    for i, d in enumerate(meeting['decisions'], 1):
        lines.append(f"{i}. {d}")
    lines.extend([
        "",
        "---",
        "",
        "## 行动项（TODO）",
        "",
        "| 序号 | 事项 | 负责人 | 截止日期 | 优先级 | 状态 |",
        "|------|------|--------|----------|--------|------|",
    ])
    for i, todo in enumerate(meeting['todos'], 1):
        lines.append(f"| {i} | {todo['item']} | {todo['owner']} | {todo['deadline']} | {todo['priority']} | ⏳ 待开始 |")
    lines.extend([
        "",
        "---",
        "",
        "## 风险提示",
        f"- {meeting['risks']}",
        "",
        "## 下次会议",
        f"- **时间**：{meeting['next_meeting'].split(' ')[0] if ' ' in meeting['next_meeting'] else meeting['next_meeting']}",
        f"- **主题**：{meeting['next_meeting'].split(' ', 1)[1] if ' ' in meeting['next_meeting'] else '待定'}",
    ])
    return "\n".join(lines)


def generate_project_docs():
    """生成项目文档"""
    docs = {}

    # 达人筛选标准
    docs["达人筛选标准 V1.0"] = """# 达人筛选标准 V1.0

## 一、筛选流程

```
简历筛选 → 视频作品评估 → 线上试镜 → 2周试用期 → 正式签约
```

## 二、评分维度

### 1. 基础素质（权重 40%）

| 指标 | 评分标准 | 分值 |
|------|----------|------|
| 形象气质 | 镜头表现力、个人风格鲜明度 | 0-20 |
| 表达能力 | 口条清晰、表达有感染力 | 0-10 |
| 专业背景 | 相关行业经验或专业资质 | 0-10 |

### 2. 内容潜力（权重 35%）

| 指标 | 评分标准 | 分值 |
|------|----------|------|
| 创意能力 | 内容选题新颖度、创意产出能力 | 0-15 |
| 制作水平 | 视频拍摄、剪辑质量 | 0-10 |
| 更新频率 | 历史内容更新稳定性 | 0-10 |

### 3. 商业潜力（权重 25%）

| 指标 | 评分标准 | 分值 |
|------|----------|------|
| 粉丝画像 | 粉丝年龄、消费能力匹配度 | 0-10 |
| 配合度 | 商务合作配合意愿和执行能力 | 0-10 |
| 成长空间 | 粉丝增长趋势、账号潜力 | 0-5 |

## 三、评分标准

- **≥80分**：优先签约，给予资源倾斜
- **60-79分**：可签约，需制定成长计划
- **<60分**：暂不签约，保持观察

## 四、试用期考核

试用期为 2 周，考核指标：
- 内容产出 ≥4 条
- 平均播放量 ≥5000
- 粉丝增长 ≥500
- 配合度评分 ≥8分

## 五、版本记录

- V1.0 (2026-03-12)：初版发布
"""

    # 内容审核规范
    docs["内容审核规范"] = """# 内容审核规范

## 一、审核流程

```
创作者自查 → PM 初审 → 合规终审 → 定时发布
```

## 二、审核清单

### 2.1 合规性检查

- [ ] 不涉及政治、宗教、色情、暴力内容
- [ ] 未经审核的医疗、金融、保健品广告已移除
- [ ] 竞品对比中无贬低他人内容
- [ ] 知识产权清晰（音乐、素材已授权）
- [ ] 广告标识符合《广告法》要求

### 2.2 品牌一致性检查

- [ ] 内容调性符合项目定位
- [ ] 达人个人人设与品牌调性一致
- [ ] 商业合作内容已标注"合作"或"广告"

### 2.3 质量标准

- [ ] 视频时长 15s-3min（根据平台调整）
- [ ] 画质 ≥1080P
- [ ] 音频清晰，无噪音
- [ ] 封面图吸引力评分 ≥7分

## 三、禁区清单

| 禁区类型 | 说明 | 处罚 |
|----------|------|------|
| 政治敏感 | 涉及政治人物、敏感事件 | 立即下架，暂停合作 |
| 虚假宣传 | 夸大产品效果、虚假承诺 | 删除内容，警告处理 |
| 侵权内容 | 未经授权使用音乐、视频 | 删除内容，赔偿处理 |
| 低俗内容 | 擦边球、暗示性内容 | 删除内容，警告处理 |
| 竞品攻击 | 直接贬低竞品品牌 | 删除内容，严重警告 |

## 四、紧急处理流程

1. **发现违规内容** → 立即下架
2. **通知相关方** → PM、达人、法务
3. **评估影响** → 确定是否需要公开声明
4. **整改措施** → 制定预防方案
5. **记录归档** → 计入达人档案
"""

    # 达人合作手册
    docs["达人合作手册"] = """# 达人合作手册

## 一、合作模式

### 1.1 签约模式

| 模式 | 说明 | 分成比例 | 适用对象 |
|------|------|----------|----------|
| 独家签约 | 达人仅与星澜合作 | 达人 60% / 公司 40% | 头部达人 |
| 非独家签约 | 达人可同时与其他机构合作 | 达人 50% / 公司 50% | 腰部达人 |
| 项目制合作 | 按单结算，无长期绑定 | 按单协商 | 临时合作 |

### 1.2 收益构成

- **基础收益**：保底薪资（签约后按月发放）
- **内容收益**：按视频播放量、互动量结算
- **商单收益**：品牌合作分成
- **奖金激励**：月度/季度绩效奖金

## 二、达人权益

- 专业内容培训（每月 2 次）
- 流量扶持（DOU+、薯条投放）
- 商务资源对接
- 法务、财务支持
- 个人品牌建设

## 三、达人义务

- 每月内容产出 ≥8 条
- 配合公司内容方向和排期
- 参加月度复盘会
- 维护个人形象，不发表不当言论
- 商业合作须经公司审核

## 四、合作流程

```
需求对接 → 方案策划 → 合同签署 → 内容制作 → 发布推广 → 数据回收 → 结算付款
```

## 五、常见问题

**Q：达人可以私自接商单吗？**
A：不可以。所有商业合作须经公司审核和签署合同。

**Q：达人可以解约吗？**
A：可以提前 30 天书面通知解约。解约后 6 个月内不得与公司竞品合作。

**Q：内容版权归谁？**
A：签约期间制作的内容版权归公司所有。达人享有署名权。
"""

    return docs


def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 项目 OnePage
    (BASE_DIR / "项目 OnePage.md").write_text(generate_onepage(), encoding="utf-8")
    print("✅ 项目 OnePage")

    # 2. 周报
    weekly_dir = BASE_DIR / "周报归档"
    weekly_dir.mkdir(exist_ok=True)
    for w in WEEKS:
        filename = f"[{w['date_range']}] Week {w['week']} 周报.md"
        (weekly_dir / filename).write_text(generate_weekly_report(w), encoding="utf-8")
        print(f"✅ Week {w['week']} 周报")

    # 3. 会议纪要
    minutes_dir = BASE_DIR / "会议纪要"
    minutes_dir.mkdir(exist_ok=True)
    for m in MEETINGS:
        filename = f"[{m['date']}] {m['title']}.md"
        (minutes_dir / filename).write_text(generate_meeting_note(m), encoding="utf-8")
        print(f"✅ {m['title']} 会议纪要")

    # 4. 项目文档
    docs_dir = BASE_DIR / "项目文档"
    docs_dir.mkdir(exist_ok=True)
    for title, content in generate_project_docs().items():
        (docs_dir / f"{title}.md").write_text(content, encoding="utf-8")
        print(f"✅ {title}")

    # 5. 数据看板（占位）
    dashboard_dir = BASE_DIR / "数据看板"
    dashboard_dir.mkdir(exist_ok=True)
    (dashboard_dir / "README.md").write_text("# 数据看板\n\n本目录存放项目数据看板截图和说明。\n\n> 数据实时更新，请查看飞书 Base 中的项目 KPI 表。\n", encoding="utf-8")
    print("✅ 数据看板 README")

    print(f"\n🎉 全部完成！共生成 {len(WEEKS)} 份周报 + {len(MEETINGS)} 份会议纪要 + 3 份项目文档 + 1 份 OnePage")
    print(f"📁 输出目录：{BASE_DIR}")


if __name__ == "__main__":
    main()
