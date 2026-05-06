---
name: route
description: "意图路由与 Agent 调度 — 识别操作类意图并调用对应 Agent 执行"
metadata:
  {
    "openclaw":
      {
        "emoji": "🔄",
      },
  }
---

# route Skill

> 意图路由与 Agent 调度 — 识别操作类意图并调用对应 Agent 执行

## 归属

- **Agent**: qa-bot
- **路径**: `agents/qa-bot/workspace/skills/route/`

## 触发条件

- 用户意图被识别为 **操作类请求**（非查询类）
- 典型指令："刷新知识库"、"生成周报"、"发通知"

## 核心能力

### 1. 意图 → Agent 映射

| 用户指令 | 目标 Agent | 调用方式 | 预期输出 |
|----------|-----------|----------|----------|
| "刷新知识库"、"同步知识库"、"/wiki-sync"、"ingest" | wiki-manager | 触发 workflow | sync_report |
| "生成周报"、"部门看板"、"周报汇总" | weekly-reporter | 触发 workflow | weekly_report |
| "发通知"、"推送卡片"、"发消息" | card-builder | 触发 workflow | card_message |

### 2. 调度执行

qa-bot 不直接执行操作，而是：
1. 识别用户意图和操作参数
2. 向用户确认："已触发 wiki-manager 执行同步，请稍等..."
3. 调用对应 Agent 的 workflow

## 调度链路

```
用户指令
    └── 意图识别（intent skill）
        └── 操作类请求 → route skill
            ├── 识别目标 Agent
            ├── 向用户确认
            └── 调用对应 Agent
                ├── wiki-manager: 执行 wiki_sync.py
                ├── weekly-reporter: 执行 weekly_report workflow
                └── card-builder: 执行 card_push workflow
```

## 调用方式

### 调用 wiki-manager

```python
# 触发 wiki-manager 的同步 workflow
# 可以通过 OpenClaw 的 agent 命令或 workflow 触发
```

### 调用 weekly-reporter

```python
# 触发 weekly-reporter 的周报生成 workflow
# 可以通过 OpenClaw 的 agent 命令或 workflow 触发
```

### 调用 card-builder

```python
# 触发 card-builder 的卡片推送 workflow
# 可以通过 OpenClaw 的 agent 命令或 workflow 触发
```

## 输出格式

**调度确认**：
```markdown
已触发 **wiki-manager** 执行知识库同步。

预计耗时：2-5 分钟
完成后将通知您同步结果。
```

**调度失败**：
```markdown
抱歉，暂时无法触发 **weekly-reporter**。

可能原因：
- 该 Agent 当前未运行
- 权限不足
- 系统维护中

建议：
- 联系管理员检查 Agent 状态
- 稍后重试
```

## 红线

- **qa-bot 不直接执行操作**，只负责调度和确认
- **不暴露其他 Agent 的内部实现细节**
- **调度前必须向用户确认**，避免误操作
- **调度失败时给出明确原因和解决建议**
