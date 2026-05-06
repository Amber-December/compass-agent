# HEARTBEAT.md — qa-bot 定时检查清单

> 心跳任务：定期自检，保持状态新鲜。

## 检查项（每次心跳轮换 2-3 项）

### 1. 知识库健康度
- [ ] wiki/ 目录是否存在 index.md
- [ ] workspace/knowledge/graph/graph.json 是否存在且非空
- [ ] 最近一次 wiki-manager 同步时间（检查 `workspace/knowledge/wiki/log.md`）

### 2. 数据新鲜度
- [ ] workspace/knowledge/data/ 目录是否有本周数据快照
- [ ] 各项目 Base 数据是否完整

### 3. 高频问题积累
- [ ] 检查 `MEMORY.md` 中 qa-bot 高频问题列表
- [ ] 是否需要更新 TOOLS.md 中的速查内容

### 4. 权限与绑定
- [ ] chatBindings 中的群是否仍然有效
- [ ] scope 映射是否需要更新（新增/删除项目群）

## 心跳策略

- **频率**：每 30 分钟检查一次
- **静默时段**：23:00 - 08:00 不主动输出
- **输出方式**：仅在有异常时报告，正常时返回 HEARTBEAT_OK