# USER.md — wiki-manager 服务信息

## 服务对象

| Agent | 消费内容 | 权限 |
|-------|---------|------|
| qa-bot | workspace/knowledge/wiki/ 知识、workspace/knowledge/data/ 数据、workspace/knowledge/graph/ 图谱 | 只读 |
| weekly-reporter | workspace/knowledge/wiki/ 知识、workspace/knowledge/data/ 数据 | 只读 |
| card-builder | 不直接消费 wiki-manager | — |

## 知识底座消费者

- **qa-bot**：回答用户问题时读取 workspace/knowledge/wiki/ 和 workspace/knowledge/data/
- **weekly-reporter**：生成周报时读取 workspace/knowledge/wiki/ 和 workspace/knowledge/data/

## 触发方式

- qa-bot 识别到 "刷新知识库" / "同步知识库" / "/wiki-sync" 时调度 wiki-manager
- 每周一 8:30 定时触发（cron）
- 每 6 小时增量检查（heartbeat）

## 飞书权限需求

- Wiki 空间读取权限
- Base 读取权限
- 不需要 IM 消息发送权限（不发消息到群）
