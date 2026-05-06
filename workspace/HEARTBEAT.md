# HEARTBEAT.md - Compass 定时任务检查清单

> 配置 OpenClaw 心跳检查，驱动 Compass 核心功能的定时触发。

---

## 每周一早晨主链路（定时触发）

### 9:00 - weekly-reporter 检查

```
检查项：
- [ ] 今天是周一
- [ ] workspace/knowledge/data/raw/ 中已有上周 Base 数据（base_YYYYMMDD.json）
- [ ] 各项目群 chat_id 已配置（TOOLS.md）

执行：
1. data-collection 采集上周数据（Base + 妙记 + Wiki）
2. risk-check 嵌入检测（weekly-reporter 内部，对比 config/scenarios/mcn.yaml 阈值）
3. 按 prompts/weekly-report.md 生成项目周报
4. wiki-manager 归档到 Wiki「周报归档」目录
5. 更新项目 OnePage 的"本周进展"和"核心 KPI"
6. card-builder 推送摘要卡片到项目群
```

### 9:05 - 部门看板推送

```
前置条件：weekly-reporter 已完成

执行（weekly-reporter 内部 dept-aggregate 子流程）：
1. 汇总 6 个项目状态（🟢🟡🔴 计数）
2. 提取部门 KPI 快照
3. 评选 Top3 知识精选（按类型/时效/跨项目价值/完整度打分）
4. 调用 card-builder 推送部门看板卡片到部门群
```

---

## 每日同步检查（心跳）

### Wiki 同步检查（每日一次）

```
检查项：
- [ ] 飞书 Wiki 是否有新增/修改文档（对比 last_sync 时间）

执行（如有变更）：
1. lark-ingest 拉取变更到 workspace/raw_lark/wiki/
2. wiki_ingest.py 重新编译变更页面
3. build_graph.py 增量更新图谱
4. 更新 workspace/knowledge/wiki/index.md 和 workspace/knowledge/wiki/log.md
```

### 风险扫描检查（每日一次，轻量）

```
检查项：
- [ ] Base 中是否有 KPI 连续下滑/越界（与 mcn.yaml 阈值对比）
- [ ] 妙记中是否有新增风险关键词（"故障"、"投诉"、"违约"等）

执行（仅发现异常时）：
1. 记录到 workspace/knowledge/data/risk_log（不入周报，等周一统一推送）
2. 如为 🔴 高风险，标记待周一重点呈现
```

---

## 心跳 vs Cron 分工

| 任务 | 方式 | 原因 |
|------|------|------|
| 周报生成（周一 9:00） | **cron** | 精确时间，独立会话 |
| 部门看板推送（周一 9:05） | **cron** | weekly-reporter 内部 dept-aggregate 子流程 |
| Wiki 同步 | **heartbeat** | 可与日常检查批量，时间可浮动 |
| 风险扫描 | **heartbeat** | 可与日常检查批量，时间可浮动 |

---

## 状态追踪

`memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "weekly_report": "2026-05-05T09:00:00Z",
    "dept_board": "2026-05-05T09:05:00Z",
    "wiki_sync": null,
    "risk_scan": null
  }
}
```
