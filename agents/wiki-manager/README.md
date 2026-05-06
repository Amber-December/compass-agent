# wiki-manager Agent 工作区

> 知识库管理 Agent — 负责飞书 Wiki 文档拉取、Base 数据同步、本地知识库维护

## 目录结构

```
agents/wiki-manager/
├── README.md              # 本文件
├── agent.json             # OpenClaw agent 配置
├── config/
│   └── sources.yaml       # Wiki 节点与 Base 表源映射配置
├── prompts/
│   ├── ingest.md          # 知识编译规范
│   └── base-sync.md       # Base 数据同步规范
├── skills/
│   └── wiki-ingest/
│       └── SKILL.md       # 知识编译 skill（完整 ingest 规范）
├── tools/                 # 可执行脚本
│   ├── wiki_ingest.py     # 知识编译（Markdown → 结构化 wiki）
│   ├── wiki_sync.py       # 飞书 Wiki 文档拉取与同步
│   ├── base_sync.py       # Base 单表同步
│   ├── base_sync_all.py   # Base 批量同步
│   ├── build_graph.py     # 知识图谱构建
│   ├── wiki_query.py      # 图增强检索
│   └── scheduler.py       # 统一调度器
├── state/                 # 同步状态与日志
│   ├── sync_state.json    # 各源 content_hash / revision
│   └── scheduler.log      # 调度器运行日志
└── raw_lark/              # 从飞书拉取的原始镜像（只读）
    ├── workspace/knowledge/wiki/              # Wiki 文档（Markdown，含 frontmatter）
    ├── base/              # Base API 原始响应（按项目分目录）
    └── minutes/           # 妙记转录文本
```

**全局输出目录**（位于 workspace 根目录，供其他 Agent 只读消费）：
- `workspace/knowledge/wiki/` — 最终知识底座（llm-wiki 标准结构）
- `workspace/knowledge/graph/` — 知识图谱数据
- `workspace/knowledge/data/` — Base 结构化数据出口

---

## 核心职责

1. **Wiki 文档拉取** — 通过 lark-cli 从飞书 Wiki/云文档获取内容 → `raw_lark/wiki/`
2. **Base 数据同步** — 通过 lark-cli 从飞书 Base 拉取多维表格 → `raw_lark/base/` + `workspace/knowledge/data/`
3. **知识编译** — 运行 wiki_ingest.py 将 Markdown → 结构化知识 → `workspace/knowledge/wiki/`
4. **索引维护** — 更新 `workspace/knowledge/wiki/index.md`，维护实体和概念图谱
5. **增量同步** — 检测变更，只重新编译修改过的文档和数据

---

## 6 个 Skill

| Skill | 职责 | 触发方式 |
|-------|------|----------|
| **lark-api** | 飞书 API 基础调用 | 全局可用 |
| **wiki-read** | Wiki 文档读取 | 全局可用 |
| **base-read** | Base 数据读取 | 全局可用 |
| **wiki-sync** | 飞书 Wiki 增量同步 | 定时 / 手动触发 |
| **base-sync** | 飞书 Base 增量同步 | 定时 / 手动触发 |
| **wiki-ingest** | 知识编译（LLM 处理） | wiki-sync 后 / 手动触发 |

### Skill 调用关系

```
定时触发 / 用户说"刷新知识库"
    └── wiki-manager
        ├── wiki-sync（检测 Wiki 变更）
        │   └── 拉取新增/修改文档 → raw_lark/wiki/
        ├── base-sync（检测 Base 变更）
        │   └── 拉取新增/修改数据 → workspace/knowledge/data/
        └── wiki-ingest（知识编译）
            └── LLM 处理 → workspace/knowledge/wiki/ + entities/ + concepts/
```

---

## 触发方式

- **用户说** "刷新知识库" / "ingest 文档" / "编译知识" / "同步 Wiki" / "知识库更新" / "/wiki-sync"
- **定时心跳**：
  - 每周一 8:30 全量同步（与 weekly-reporter 9:00 对齐）
  - 每 6 小时增量检查

---

## 工作流

### Wiki 文档线（知识）

```
飞书 Wiki 节点列表（按配置的 scope 过滤）
    │
    ▼
wiki_sync.py → lark-cli docs +fetch → agents/wiki-manager/raw_lark/wiki/<node_id>.md
    │
    ▼
content-hash / 修改时间 对比 sync_state.json
    │
    ├─ 无变化 → 跳过
    └─ 有变化 → 进入 ingest
              │
              ▼
        wiki-ingest skill（LLM 按 ingest.md 规范处理）
              │
              ▼
        输出到 workspace/knowledge/wiki/{scope}/sources/<slug>.md
              │
              ▼
        更新 workspace/knowledge/wiki/index.md、workspace/knowledge/wiki/log.md
              │
              ▼
        build_graph.py（增量或全量重建 graph.json）
```

### Base 数据线（结构化）

```
飞书 Base 表列表（按 schema/*.yaml 注册）
    │
    ▼
base_sync.py → lark-cli base +record-list → agents/wiki-manager/raw_lark/base/<project>/<table>.json
    │
    ▼
规范化处理（展平嵌套字段、统一日期格式、空值处理）
    │
    ▼
输出为 workspace/knowledge/data/<project>/<table>.json
    │
    │   结构：数组对象 [{field: value, ...}, ...]
    │   元数据：同级 <table>_meta.json（table_token, synced_at, record_count, content_hash）
    ▼
更新 sync_state.json（记录每张表的 hash、时间、状态）
    │
    ▼
供 weekly-reporter（聚合分析）和 qa-bot（实时查询）读取
```

**Base 数据不进入 workspace/knowledge/wiki/ 目录**，与知识文档物理隔离。

---

## 与 qa-bot 的关系

- **qa-bot 只读**：查询时读取 `workspace/knowledge/wiki/` 和 `workspace/knowledge/data/` 下的结果
- **wiki-manager 只写**：所有飞书交互、知识编译和数据同步由 wiki-manager 负责
- **解耦**：qa-bot 不依赖 lark-cli，wiki-manager 不处理对话逻辑

---

## OpenClaw 集成

- `agent.json` 定义了 wiki-manager 的 triggers、skills、systemPrompt
- OpenClaw agent 运行时从本目录读取配置，执行知识同步任务
- `prompts/ingest.md` 与 `tools/wiki_ingest.py` 共享同一套 Wiki ingest 规范
- `prompts/base-sync.md` 与 `tools/base_sync.py` 共享同一套 Base 同步规范

---