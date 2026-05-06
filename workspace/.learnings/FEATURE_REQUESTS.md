# Feature Requests

## [FEAT-20260505-001] wiki_ingest 增量检测优化

**Logged**: 2026-05-05T22:15:00+08:00
**Priority**: medium
**Status**: pending
**Area**: backend

### Requested Capability
wiki_ingest.py 目前每次运行都重新处理所有 139 个文档，即使内容未变更。需要真正的增量检测：
1. 基于 content_hash 跳过未变更文件
2. 记录上次处理时间戳
3. 只处理新增或修改的文件

### User Context
139 个文档的 ingest 耗时较长，且重复生成相同的输出

### Complexity Estimate
medium

### Suggested Implementation
- 在 wiki/ 目录下创建 .sync_state.json
- 记录每个 source 文件的 content_hash 和 last_ingested_at
- ingest 前对比 hash，相同则跳过

---

## [FEAT-20260505-002] 实体提取增强

**Logged**: 2026-05-05T22:15:00+08:00
**Priority**: low
**Status**: pending
**Area**: backend

### Requested Capability
当前实体提取只支持简单正则，需要：
1. 从表格中提取 PM、负责人等信息
2. 从会议记录中提取参会人
3. 从 Base 数据中提取品牌、达人信息

### User Context
周报和会议纪要有大量结构化数据，正则无法有效提取

### Complexity Estimate
medium

### Suggested Implementation
- 针对周报模板优化提取规则
- 针对会议纪要模板提取参会人和决策
- 考虑使用 LLM 辅助提取（复杂场景）

---

## [FEAT-20260505-003] 知识图谱可视化

**Logged**: 2026-05-05T22:15:00+08:00
**Priority**: low
**Status**: pending
**Area**: frontend

### Requested Capability
将 wiki/ 中的实体和概念关系可视化为图谱

### User Context
便于理解知识结构和发现关联

### Complexity Estimate
medium

### Suggested Implementation
- 使用 D3.js 或 ECharts 渲染
- 从 knowledge/wiki/entities/ 和 knowledge/wiki/concepts/ 读取节点
- 从 [[wikilink]] 解析边

---
