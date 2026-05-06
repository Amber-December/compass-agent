---
name: data-collection
description: "数据采集 — 从飞书 Base、Wiki、妙记采集项目数据，为周报生成提供原料"
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
      },
  }
---

# data-collection Skill

> 数据采集 — 从飞书 Base、Wiki、妙记采集项目数据，为周报生成提供原料

## 归属

- **Agent**: weekly-reporter
- **路径**: `agents/weekly-reporter/workspace/skills/data-collection/`

## 触发条件

- 周报生成前自动执行
- 手动触发数据更新

## 核心能力

### 1. Base 数据采集

从飞书多维表格拉取项目 KPI、任务状态、达人数据等：

```bash
lark-cli base records list --params '{"app_token":"xxx","table_id":"xxx"}'
```

### 2. Wiki 数据采集

读取项目 Wiki 中的最新文档、会议纪要：

```bash
lark-cli docs +fetch --doc <obj_token> --format pretty
```

### 3. 妙记数据采集

提取会议纪要和待办事项。

## 输出

采集的数据保存到 `workspace/knowledge/data/<project>/` 目录，供周报生成使用。
