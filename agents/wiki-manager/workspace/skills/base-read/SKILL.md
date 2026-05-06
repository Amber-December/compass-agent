---
name: base-read
description: "base-read"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 读取飞书 Base（多维表格）数据，供 wiki-manager 及其他 Agent 消费结构化数据

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/base-read/`

## 能力

- 列出 Base 中的表格
- 按条件查询记录
- 获取字段定义
- 导出记录到本地 JSON 快照

## 使用方法

```bash
# 列出记录
lark-cli base +record-list --base-token=<token> --table-id=<table>

# 获取字段定义
lark-cli base +field-list --base-token=<token> --table-id=<table>
```

## 数据输出

结构化快照保存到 `workspace/knowledge/data/<project>/<table>.json`，同级目录下附带 `<table>_meta.json`（含 table_token、synced_at、record_count、content_hash）。

## 权限

- `bitable:record:readonly`
- `bitable:table:readonly`
