# Shared 共享组件

本目录存放所有 Agent 共享的能力、工具和配置。

## 目录说明

| 目录 | 内容 | 说明 |
|------|------|------|
| `skills/` | 共享 Skill 设计文档 | 通用能力的定义（实际运行时在 `workspace/skills/` 下） |
| `prompts/` | 通用 Prompt 模板 | 跨 Agent 复用的 prompt |
| `utils/` | 工具函数 | 通用代码辅助函数 |

## 共享 Skills 清单

| Skill | 说明 | 使用 Agent |
|-------|------|-----------|
| lark-api | 飞书 API 基础封装 | 全部 |
| data-collection | 数据采集 | weekly-reporter, risk-monitor, dept-aggregator, efficiency-analyzer |
| analytics | 数据分析 | efficiency-analyzer |
| insight-llm | LLM 洞察生成 | efficiency-analyzer |
| card-builder | 飞书卡片构建 | weekly-reporter, dept-aggregator, efficiency-analyzer |
| threshold-check | 阈值检查 | risk-monitor, efficiency-analyzer |
| prompt-template | Prompt 模板管理 | 全部 |
| intent-classifier | 意图识别 | qa-bot |
