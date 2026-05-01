# Agents 目录

本目录存放 Compass（司南）多 Agent 架构中的各个 Agent 配置和文档。

## Agent 列表

| Agent | 目录 | 核心职责 | 触发方式 |
|-------|------|----------|----------|
| wiki-manager | [wiki-manager/](wiki-manager/) | 知识库管理 | 人工/定时 |
| weekly-reporter | [weekly-reporter/](weekly-reporter/) | 周报合成 | 每周一 9:00 |
| risk-monitor | [risk-monitor/](risk-monitor/) | 风险检测 | 与周报一起 |
| dept-aggregator | [dept-aggregator/](dept-aggregator/) | 部门聚合 | 每周一 9:05 |
| qa-bot | [qa-bot/](qa-bot/) | 自然查询 | 群内 @ |
| efficiency-analyzer | [efficiency-analyzer/](efficiency-analyzer/) | 效能分析 | 定时/人工 |

## 目录说明

每个 Agent 目录包含：
- `README.md` — Agent 职责、输入输出、依赖说明
- `prompts/` — Agent 专属的 prompt 模板
- `docs/` — Agent 的设计文档和运行记录

## Skills 位置

所有 Skills 统一存放在 `workspace/skills/` 目录下，由 OpenClaw 运行时加载。
