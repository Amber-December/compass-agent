# Compass 集成 LLM-Wiki-Agent 方案分析

## 一、方案核心：不用向量库的知识管理

llm-wiki-agent 采用**"符号化知识编译"**替代传统的 RAG 向量检索：

```
传统 RAG                    LLM Wiki Agent
─────────────────           ─────────────────────────
文档 → 分块 → Embedding      文档 → LLM 结构化提取
         ↓                          ↓
    向量数据库                  结构化 Markdown 页面
         ↓                          ↓
    相似度检索                  关键词匹配 + 图遍历
         ↓                          ↓
    Top-k 文本块                完整相关页面
         ↓                          ↓
    LLM 回答                    LLM 综合回答
```

**核心差异**：它不是"检索片段再拼接"，而是让 LLM 在 ingest 阶段就把知识**编译**成结构化的、带交叉引用的 Wiki 页面，查询时直接读取完整的结构化页面做综合。

---

## 二、llm-wiki-agent 的三大利器

### 2.1 ingest.py — 知识编译器

把任意文档（PDF/Word/妙记/Markdown）喂给 LLM，输出：

```
wiki/
├── sources/     ← 每份源文档的摘要页（含 [[Wikilink]] 内链）
├── entities/    ← 自动提取的实体页（达人、品牌、项目、PM）
├── concepts/    ← 自动提取的概念页（SOP、方法论、规范）
├── overview.md  ← 跨所有源的全局综合（每次 ingest 自动更新）
├── index.md     ← 目录索引（自动维护）
└── log.md       ← 操作日志（可溯源）
```

**对 Compass 的价值**：
- 飞书 Wiki 的会议纪要、项目文档、周报 → 经过 ingest → 变成带内链的结构化知识页
- ingest 时会**自动检测矛盾**（如新会议纪要推翻旧决策）
- 实体页自动累积：每次提到"李小明"都会在 entities/李小明.md 中追加新信息

### 2.2 query.py — 图增强检索

查询时不走向量相似度，而是：

1. **关键词匹配**：从 index.md 的链接标题中匹配问题关键词（支持 CJK 双字滑动窗口）
2. **图邻居扩展**：读取 graph.json，找到匹配页的关联页（confidence ≥ 0.7 的边）
3. **LLM 综合**：把相关完整页面（不是碎片）喂给 LLM 生成答案

**对 Compass 的价值**：
- qa-bot 可以直接复用这套查询逻辑
- 跨项目查询时，图遍历能自然找到关联（如"垂类达人孵化"和"品牌代运营"通过"雅诗兰黛"实体连接）

### 2.3 build_graph.py — 知识图谱可视化

两-pass 建图：
- **Pass 1（确定式）**：解析所有 `[[wikilink]]` → EXTRACTED 边
- **Pass 2（语义式）**：LLM 推断隐式关系 → INFERRED/AMBIGUOUS 边（带 confidence）

输出 `graph/graph.html` — 自包含的可交互可视化，支持：
- 搜索节点
- 按边类型/置信度过滤
- 点击节点高亮邻居并展示 Markdown 内容
- Louvain 社区检测聚类

**对 Compass 的价值**：
- 可用于演示"团队大脑"的可视化
- 社区检测能自动发现项目间的隐性关联

---

## 三、与 Compass 多 Agent 架构的集成点

### 3.1 数据流改造：从 raw/ 到飞书生态

llm-wiki-agent 的数据源是 `raw/` 下的本地文件。Compass 需要改为**飞书生态**：

```
飞书 Wiki 文档          飞书妙记              飞书 Base
     │                    │                    │
     ▼                    ▼                    ▼
wiki-manager 拉取     weekly-reporter 提取    data-collection 导出
     │                    │                    │
     └────────────────────┼────────────────────┘
                          ▼
              统一写入 workspace/raw_lark/
                          │
                          ▼
                   ingest.py 编译
                          │
                          ▼
                    wiki/sources/
                    wiki/entities/
                    wiki/concepts/
```

**改造点**：
1. 新增 `tools/lark_ingest.py`（P2 负责）负责从飞书拉取内容到 `workspace/raw_lark/`
2. `ingest.py` 的输入从 `raw/` 改为 `workspace/raw_lark/`
3. 需要把飞书文档的 URL 保留在 source page 中，方便 qa-bot 回答时引用

### 3.2 Agent 调用关系

```
wiki-manager（新增职责）
    ├── 原有：本地 Markdown ↔ 飞书 Wiki 双向推送
    └── 新增：定期 ingest 飞书内容到本地 LLM-Wiki
            │
            ├── 输出 wiki/sources/ → 供 qa-bot 检索
            ├── 输出 wiki/entities/ → 供 qa-bot 回答人/项目/品牌相关问题
            ├── 输出 wiki/concepts/ → 供 qa-bot 回答 SOP/方法论问题
            └── 输出 graph/graph.html → 供可视化展示

weekly-reporter
    ├── 原有：读取 Base 数据生成周报
    └── 新增：生成的周报 Markdown 也要被 wiki-manager ingest
            │    （这样 qa-bot 能回答"上周做了什么"）
            └── 依赖 wiki-manager 提供知识底座状态

qa-bot（直接复用 query.py 逻辑）
    ├── 接收群 @ 消息
    ├── 调用 query.py 同款检索（关键词 + 图邻居）
    ├── 从 wiki/ 中读取相关完整页面
    └── LLM 综合生成带飞书链接引用的答案

dept-aggregator
    ├── 原有：聚合项目周报
    └── 新增：Top3 精选可借助 graph 的社区检测发现跨项目关联
```

### 3.3 与 OnePage / 周报 / 会议纪要 / 数据看板的关系

| 文档类型 | 在 LLM-Wiki 中的角色 | 维护方式 |
|---------|-------------------|---------|
| **OnePage** | 不直接 ingest，因为它是聚合快照而非原始知识 | weekly-reporter 生成周报后反向更新 |
| **周报** | 作为 source 被 ingest → `wiki/sources/week-9-report.md` | weekly-reporter 生成后自动触发 ingest |
| **会议纪要** | 作为 source 被 ingest → `wiki/sources/2026-04-21-review-meeting.md` | wiki-manager 从飞书同步后触发 ingest |
| **项目文档** | 作为 source 被 ingest → `wiki/sources/kol-selection-criteria.md` | wiki-manager 从飞书同步后触发 ingest |
| **数据看板** | 不直接 ingest，数据看板是 Base 数据的可视化 | 通过 Base 表查询获取 |

**关键设计**：
- OnePage 和数据看板是**聚合层**（从其他数据计算而来），不需要进入知识底座
- 周报、会议纪要、项目文档是**原始知识层**，需要被 ingest 供 qa-bot 检索
- ingest 时会自动提取周报中的实体（达人名、品牌名）和概念（整改方案、流量投放），生成实体页和概念页

---

## 四、方案优劣分析

### 4.1 优势（与向量库方案对比）

| 维度 | 向量库 RAG | LLM Wiki Agent |
|------|-----------|----------------|
| **依赖** | 需要 embedding 模型 + 向量数据库 | 纯 Markdown 文件，零依赖 |
| **知识结构** | 文本块，无结构 | 结构化页面（实体/概念/来源），带交叉引用 |
| **矛盾检测** | 无 | ingest 时自动检测新旧知识矛盾 |
| **可解释性** | "这块文本相似" | "这个实体在 5 个来源中被提及" |
| **可视化** | 难以可视化 | 直接生成可交互知识图谱 |
| **增量更新** | 重新 embedding | 只需重新 ingest 变更的页面 |
| **中文支持** | 依赖 embedding 模型质量 | query.py 内置 CJK 双字滑动窗口匹配 |

### 4.2 劣势与风险

| 风险 | 说明 | 缓解方案 |
|------|------|---------|
| **Token 消耗高** | query 时可能读取多个完整页面（而非 top-k 块），上下文长度压力大 | 限制最多 15 个相关页；优先读 overview + index 做粗筛 |
| **检索精度有限** | 关键词匹配不如向量相似度精准，可能漏掉语义相关但字面上不匹配的内容 | 结合 graph 邻居扩展；必要时增加一步 LLM 重排序 |
| **ingest 成本高** | 每份文档都要调 LLM 做结构化提取，大批量文档时费用高 | 增量 ingest（只处理变更文档）；缓存 SHA256 |
| **实时性** | Wiki 内容有滞后（需要等 wiki-manager 同步 + ingest） | 高频定时同步（每小时）；qa-bot 对实时数据直接查 Base |

### 4.3 关键结论

**这个方案非常适合 Compass**：
1. MCN 场景的知识量是**有限且结构化**的（6 个项目 × 9 周 ≈ 几百篇文档），不是海量非结构化数据
2. 知识的价值在于**关联性**（达人与品牌的关系、会议决策与后续执行的关系），图结构恰好擅长表达
3. 不引入向量数据库降低了部署复杂度，对比赛 Demo 更友好

**建议的混合策略**：
- **知识查询**（SOP、会议纪要、历史周报）→ LLM Wiki 的 query.py 模式
- **实时数据查询**（本周 KPI、任务状态）→ 直接查 Base 表
- **跨项目聚合**（部门看板）→ 读取 weekly-reporter 的输出

---

## 五、落地建议：最小可行集成

### Step 1：目录结构调整

在 Compass 项目中新增：

```
lark-knowledge-agent/
├── wiki/                          ← 本地 LLM-Wiki 知识底座
│   ├── sources/                   ← 飞书文档 ingest 后的结构化页面
│   ├── entities/                  ← 实体页（达人、PM、品牌）
│   ├── concepts/                  ← 概念页（SOP、方法论）
│   ├── index.md                   ← 自动维护的目录
│   ├── overview.md                ← 全局综合
│   └── log.md                     ← 操作日志
│
├── graph/                         ← 知识图谱
│   ├── graph.json
│   └── graph.html
│
├── workspace/
│   └── raw_lark/                  ← 从飞书拉取的原始文档（待 ingest）
│       ├── wiki/                  ← 飞书 Wiki 文档
│       ├── minutes/               ← 飞书妙记转录
│       └── base_exports/          ← Base 表导出（CSV/JSON）
│
└── tools/
    ├── lark_ingest.py             ← 从飞书拉取到 workspace/raw_lark/（P2）
    ├── wiki_ingest.py             ← 参考 llm-wiki-agent 的 ingest.py，适配 Compass
    ├── wiki_query.py              ← 参考 llm-wiki-agent 的 query.py，供 qa-bot 调用
    └── build_graph.py             ← 直接复用 llm-wiki-agent 的 build_graph.py
```

### Step 2：关键改造清单

| 改造项 | 工作量 | 负责 |
|--------|--------|------|
| 把 `ingest.py` 的 `raw/` 路径改为 `workspace/raw_lark/` | 小 | P1/P2 |
| 在 source page 中保留飞书原始 URL，供 qa-bot 引用 | 小 | P1 |
| 把 `query.py` 包装成 qa-bot 可调用的函数 | 中 | P2 |
| `lark_ingest.py`：飞书 Wiki → raw_lark/ 的拉取脚本 | 中 | P2 |
| weekly-reporter 生成周报后自动触发 wiki_ingest | 小 | P2 |
| 中文分词优化（CJK 已支持，可进一步增强） | 小 | P1 |

### Step 3：与现有 prompt 模板的衔接

qa-bot 的 prompt（`prompts/mcn/qa-bot.md`）中关于"检索到的 Wiki 片段"的输入变量：

```
- 检索到的 Wiki 片段：{{wiki_chunks}}
```

实际实现时，`wiki_chunks` 不是向量检索的文本块，而是 `wiki_query.py` 返回的**完整相关页面列表**（含页面路径和 Markdown 内容）。qa-bot prompt 不需要改，只需替换数据获取逻辑。

---

## 六、参考资源

- 原始项目：`/Users/amber/Downloads/llm-wiki-agent-main/`
- 核心文件：
  - `tools/ingest.py` — 知识编译
  - `tools/query.py` — 图增强检索
  - `tools/build_graph.py` — 知识图谱构建
  - `CLAUDE.md` — 维护 schema 定义
- 依赖：`litellm`（LLM 调用）、`markitdown`（格式转换）、`networkx`（图算法）

---

*分析日期：2026-05-01 | 建议优先级：高（与 weekly-reporter / qa-bot 直接相关）*
