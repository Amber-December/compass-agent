# qa-bot Skills 索引

> 5 个 Skill，覆盖意图识别 → 知识/数据/图谱查询 → Agent 调度的完整链路。

---

## Skill 清单

| Skill | Emoji | 职责 | 目标 Agent |
|-------|-------|------|-----------|
| [intent](intent/) | 🎯 | 意图识别 — 分析用户输入，判断意图类别 | qa-bot |
| [query](query/) | 📚 | 知识查询 — 基于 wiki/ 回答知识类问题 | qa-bot |
| [data-query](data-query/) | 📊 | 数据查询 — 基于 data/ 回答数据类问题 | qa-bot |
| [graph-query](graph-query/) | 🕸️ | 图谱查询 — 展示/描述知识图谱 | qa-bot |
| [route](route/) | 🔄 | 意图路由 — 调度操作类请求给其他 Agent | wiki-manager / weekly-reporter / card-builder |

## 调用链路

```
用户输入
    └── intent 🎯（意图识别）
        ├── 知识查询 ──→ query 📚 ──→ wiki_query.py
        ├── 数据查询 ──→ data-query 📊 ──→ data_query.py
        ├── 图谱查询 ──→ graph-query 🕸️ ──→ graph_query.py
        ├── 个人介绍 ──→ query 📚（直接返回模板）
        ├── 闲聊 ──────→ query 📚（礼貌引导）
        └── 操作类 ────→ route 🔄 ──→ 调度其他 Agent
            ├── 刷新知识库 ──→ wiki-manager
            ├── 生成周报 ────→ weekly-reporter
            └── 推送卡片 ────→ card-builder
```

## 工具脚本

所有 Skill 依赖的工具脚本位于 `../tools/`：

| 工具 | 对应 Skill | 功能 |
|------|-----------|------|
| `wiki_query.py` | query | 知识库检索 |
| `data_query.py` | data-query | 数据检索 |
| `graph_query.py` | graph-query | 图谱检索 + 子图生成 + HTTP 服务 |

## 设计原则

1. **工具只做数据检索**，返回上下文文本，不直接生成回答
2. **LLM 生成回答**在 OpenClaw 主链路中完成，工具只提供素材
3. **职责分离**：查询类 qa-bot 自己处理，操作类调度给其他 Agent
4. **权限隔离**：所有查询工具都支持 `scope` 参数过滤
