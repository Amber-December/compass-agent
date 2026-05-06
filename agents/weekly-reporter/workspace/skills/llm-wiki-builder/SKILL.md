---
name: llm-wiki-builder
description: "LLM 知识构建 — 利用大模型理解、提炼和结构化知识内容"
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
      },
  }
---

# llm-wiki-builder Skill

> LLM 知识构建 — 利用大模型理解、提炼和结构化知识内容

## 归属

- **Agent**: weekly-reporter
- **路径**: `agents/weekly-reporter/workspace/skills/llm-wiki-builder/`

## 核心能力

### 1. 内容理解与提炼

使用 LLM 对采集到的原始数据进行理解和提炼：
- 从会议纪要中提取关键决策和行动项
- 从 Base 数据中识别趋势和异常
- 从 Wiki 文档中提取项目进展

### 2. 结构化生成

将提炼后的内容按模板结构化为周报格式：
- Markdown 格式的项目周报
- 结构化的部门看板
- 风险摘要和预警

## 使用方式

调用 OpenClaw 配置的 LLM 接口生成内容，配合 prompt-template skill 的模板使用。
