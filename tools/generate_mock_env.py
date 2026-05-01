#!/usr/bin/env python3
"""
星流科技模拟环境生成器
=========================
用途：为比赛构建虚拟的企业办公环境
注意：本脚本属于环境搭建工具，不随项目核心代码提交到 Git

功能规划：
1. 在飞书 Wiki 知识库批量创建部门文档（技术方案、周报、会议纪要等）
2. 生成模拟任务数据（保存到本地 JSON）
3. 生成模拟日历数据（保存到本地 JSON）
4. 生成项目看板数据（保存到本地 JSON）

使用方法：
    python tools/generate_mock_env.py

输出位置：
    data/raw/mock_tasks.json      ← 模拟任务
    data/raw/mock_calendar.json   ← 模拟日历
    data/raw/mock_bitable.json    ← 模拟项目看板
    data/raw/weekly_summary.json  ← 本周摘要

依赖：
    - lark-cli（已配置好 App ID / App Secret）
    - Python 3.9+
"""

import json
import random
import subprocess
import time
from datetime import datetime, timedelta

# ==================== 企业配置 ====================
COMPANY_NAME = "星流科技"
TEAM_NAME = "研发二部"
TEAM_SIZE = 8

# 本周时间范围（模拟数据的时间基准）
WEEK_START = datetime(2026, 4, 21)  # 周一
WEEK_END = datetime(2026, 4, 27)    # 周日

# 虚拟团队成员（8人）
MEMBERS = [
    {"name": "陈志强", "role": "研发经理", "email": "chenzhiqiang@starflow.com"},
    {"name": "林小雅", "role": "高级后端工程师", "email": "linxiaoya@starflow.com"},
    {"name": "王浩然", "role": "后端工程师", "email": "wanghaoran@starflow.com"},
    {"name": "张思远", "role": "前端负责人", "email": "zhangsiyuan@starflow.com"},
    {"name": "刘子涵", "role": "前端工程师", "email": "liuzihan@starflow.com"},
    {"name": "赵文博", "role": "算法工程师", "email": "zhaowenbo@starflow.com"},
    {"name": "孙晓雯", "role": "测试工程师", "email": "sunxiaowen@starflow.com"},
    {"name": "周凯文", "role": "运维工程师", "email": "zhoukaiwen@starflow.com"},
]

# 模拟项目（4个）
PROJECTS = [
    {"name": "智能客服系统V3", "code": "Project-Copilot", "status": "进行中", "progress": 68,
     "milestone": "5月15日上线", "risk": "API接口延迟风险", "risk_level": "中"},
    {"name": "企业数据中台重构", "code": "Project-DataHub", "status": "进行中", "progress": 45,
     "milestone": "6月30日交付", "risk": "数据迁移复杂度高", "risk_level": "高"},
    {"name": "移动端APP 3.0改版", "code": "Project-MobileX", "status": "收尾中", "progress": 92,
     "milestone": "4月30日提测", "risk": "无", "risk_level": "低"},
    {"name": "AI知识图谱构建", "code": "Project-KG", "status": "调研中", "progress": 15,
     "milestone": "5月20日方案评审", "risk": "技术选型未定", "risk_level": "高"},
]


# ==================== 功能模块（待实现） ====================

def create_wiki_space():
    """
    TODO: 在飞书创建「研发二部知识库」Wiki Space
    命令: lark-cli wiki spaces create --name "研发二部知识库"
    """
    pass


def create_wiki_nodes():
    """
    TODO: 在 Wiki Space 下创建目录节点（文件夹）
    目录结构:
        01-项目管理
        02-技术方案
        03-会议纪要与决策
        04-团队规范
        05-最佳实践与踩坑记录
        06-培训与分享
    """
    pass


def create_docs():
    """
    TODO: 批量创建飞书文档到 Wiki 节点
    约 15-20 篇，包括:
        - 技术方案评审纪要（4篇，每个项目1篇）
        - 项目周报（4篇）
        - 会议纪要（3-4篇）
        - 团队规范（3篇）
        - 最佳实践（2-3篇）
        - 培训分享（1-2篇）
    使用 lark-cli docs +create 命令
    """
    pass


def generate_mock_tasks():
    """
    TODO: 生成模拟任务数据，保存到 data/raw/mock_tasks.json
    约 40-60 个任务，覆盖:
        - 不同状态: completed / in_progress / overdue / todo
        - 不同优先级: 高 / 中 / 低
        - 不同负责人: 8个成员随机分配
        - 不同项目: 4个项目随机分配
    """
    pass


def generate_mock_calendar():
    """
    TODO: 生成模拟日历数据，保存到 data/raw/mock_calendar.json
    约 15-20 个会议，覆盖:
        - 不同类型: 站会 / 周会 / 评审会 / 对齐会
        - 不同参与人数: 3-6人
        - 不同时长: 30min / 45min / 60min / 90min
        - 周一到周五分布
    """
    pass


def generate_mock_bitable():
    """
    TODO: 生成模拟项目看板数据，保存到 data/raw/mock_bitable.json
    4 条项目记录，包含:
        - 项目名称、状态、进度
        - 里程碑、风险项
        - 负责人、本周完成任务数
    """
    pass


def generate_summary():
    """
    TODO: 生成本周数据摘要，保存到 data/raw/weekly_summary.json
    供 OpenClaw 快速了解模拟环境概况
    """
    pass


# ==================== 主入口 ====================

if __name__ == "__main__":
    print(f"🚀 星流科技模拟环境生成器")
    print(f"   企业: {COMPANY_NAME}")
    print(f"   部门: {TEAM_NAME} ({TEAM_SIZE}人)")
    print(f"   项目: {len(PROJECTS)}个")
    print(f"   时间: {WEEK_START.strftime('%Y-%m-%d')} ~ {WEEK_END.strftime('%Y-%m-%d')}")
    print(f"\n⚠️  本脚本尚未实现，请先完成各 TODO 函数")
    print(f"   完成后执行: python tools/generate_mock_env.py")
