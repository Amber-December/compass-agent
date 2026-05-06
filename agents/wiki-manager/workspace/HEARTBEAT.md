# HEARTBEAT.md — wiki-manager 定时检查清单

> 心跳任务：定期自检，保持知识底座新鲜。

## 检查项（每次心跳轮换）

### 1. 增量同步检查（每 6 小时）
- [ ] 飞书 Wiki 是否有新增/修改文档（对比 last_sync 时间）
- [ ] 飞书 Base 是否有数据更新

执行（如有变更）：
1. wiki_sync.py 增量拉取变更到 raw_lark/
2. wiki_ingest.py 重新编译变更页面
3. build_graph.py 增量更新图谱
4. base_sync_all.py 同步 Base 数据
5. 更新 workspace/knowledge/wiki/log.md 和 sync_state.json

### 2. 知识库健康度检查
- [ ] workspace/knowledge/wiki/ 目录是否存在 index.md
- [ ] workspace/knowledge/graph/graph.json 是否存在且非空
- [ ] workspace/knowledge/data/base_snapshot/ 是否有各项目数据

### 3. 状态一致性检查
- [ ] sync_state.json 中的 content_hash 是否与实际文件一致
- [ ] 是否有 orphaned 文件（sync_state 中有但本地已删）
- [ ] lock 文件是否残留（上次同步异常退出）

## 心跳策略

- **频率**：每 6 小时检查一次（0 */6 * * *）
- **静默时段**：无静默要求，但避免凌晨 2:00-5:00 执行全量同步
- **输出方式**：仅在有变更或异常时记录日志，正常时静默

## 全量同步（每周一 8:30 cron）

与 weekly-reporter 9:00 对齐，确保周报生成前知识底座已更新：

```
8:30  wiki-manager 全量同步
      ├─▶ 拉取所有 Wiki 文档
      ├─▶ 全量知识编译
      ├─▶ 全量 Base 同步
      ├─▶ 构建图谱
      └─▶ 更新 sync_state.json

9:00  weekly-reporter 读取 workspace/knowledge/wiki/ + workspace/knowledge/data/ 生成周报
```
