---
name: prompt-template
description: "提示词模板管理 — 周报生成、部门看板的 LLM Prompt 模板库"
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
      },
  }
---

# prompt-template Skill

> 提示词模板管理 — 周报生成、部门看板的 LLM Prompt 模板库

## 归属

- **Agent**: weekly-reporter
- **路径**: `agents/weekly-reporter/workspace/skills/prompt-template/`

## 核心能力

### 1. 项目周报模板

根据场景配置（config/scenarios/*.yaml）生成结构化 Prompt：

- 项目基本信息
- 本周任务完成情况
- KPI 数据摘要
- 风险与问题
- 下周计划

### 2. 部门看板模板

汇总多个项目的周报，生成部门级看板：

- N 个项目状态（🟢🟡🔴）
- Top3 知识精选
- 部门级风险预警

## 使用方式

Prompt 模板位于 `agents/weekly-reporter/prompts/` 目录，按场景分类管理。
