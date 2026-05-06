# Compass（司南）— MCN 事业部 AI 知识中枢

> **一句话定位**：一个懂业务、有边界、会协作的 AI 团队效能助手，让项目群里的每个问题都能在 10 秒内得到精准回答。

---

## 一、我们解决了什么问题？

### 真实痛点

在 MCN 事业部，6 个项目并行运营（垂类达人孵化、品牌代运营、直播电商、短视频内容矩阵、虚拟 IP 孵化、达人私域运营）。每个项目都有：

- **上百份 Wiki 文档**（SOP、会议纪要、周报、项目文档）
- **多张 Base 数据表**（达人档案、周度 KPI、内容产出、合作记录）
- **跨项目协作需求**（部门周报需要汇总各项目数据）

**传统工作流的困境**：

| 场景 | 旧方式 | 耗时 |
|------|--------|------|
| 新人问"达人筛选标准是什么" | 翻找 Wiki，可能找到旧版本 | 5-15 分钟 |
| 项目经理问"这周 GMV 多少" | 打开 Base，切表，筛选，计算 | 3-10 分钟 |
| 想看某个项目的知识全貌 | 手动整理文档，手动画关系图 | 1-2 小时 |
| 跨项目打听数据 | 私聊其他项目组，等待回复 | 数小时 |
| 写部门周报 | 逐个群收集数据，复制粘贴汇总 | 半天 |

**核心矛盾**：信息分散在飞书 Wiki、飞书 Base、群聊记录三个地方，人和信息之间没有高效的连接层。

### 解决方案

Compass（司南）= **群聊入口 + AI 推理 + 知识底座 + 权限隔离**

用户在项目群里 @司南 提问，系统根据当前群聊自动识别项目范围，调用知识检索、数据查询或图谱生成，秒级返回精准答案。

```
Before: 员工提问 → 找文档/翻表格/问同事 → 等待 → 获得答案（10min~1h）
After:  员工提问 → @司南 → 意图识别 → 知识检索/数据查询/图谱生成 → 秒级回复
```

---

## 二、系统架构：4-Agent 协作编排

Compass 不是单一的聊天机器人，而是一个**基于 OpenClaw 框架的多 Agent 协作系统**。我们刻意将系统拆分为 4 个独立 Agent，而非做一个"全能单体 AI"。

### 2.1 设计哲学：为什么不是单体 AI？

**单体 AI 的局限性**：
- **职责混杂**：一个 Prompt 里既要处理意图识别、又要做数据查询、还要生成周报，上下文爆炸，效果递减
- **无法独立演进**：改周报模板可能影响问答质量，改数据查询逻辑可能破坏闲聊体验
- **单点故障**：一个 Agent 崩溃 = 整个系统不可用
- **权限边界模糊**：问答和数据同步混在一起，容易在 Prompt 层面就泄露敏感信息

**多 Agent 的优势**：
- **单一职责**：每个 Agent 只做一件事，Prompt 聚焦，效果更稳定
- **独立演进**：wiki-manager 的同步逻辑升级不影响 qa-bot 的问答表现
- **能力可组合**：qa-bot 像"调度中心"一样调用其他 Agent，类似微服务架构
- **权限物理隔离**：敏感数据同步（wiki-manager）和问答入口（qa-bot）是不同进程，不会在 Prompt 层面交叉

### 2.2 OpenClaw 编排框架核心机制

OpenClaw 是轻量级 Agent 编排层，提供以下关键机制：

| 机制 | 作用 | 在 Compass 中的体现 |
|------|------|-------------------|
| `entryPoint` | 定义用户入口 Agent | `qa-bot` 是唯一的 entryPoint，所有用户消息先到 qa-bot |
| `delegatesTo` | 定义可调度目标 | qa-bot 可以委派给 wiki-manager、weekly-reporter、card-builder |
| `canBeCalledBy` | 定义调用权限 | wiki-manager 只能被 qa-bot 调用，防止外部直接触发敏感操作 |
| `skills` | 注册 Agent 能力 | 每个 Agent 声明自己拥有的技能列表，OpenClaw 按需加载 |
| `triggers` | 关键词触发 | "刷新知识库" → wiki-manager；"生成周报" → weekly-reporter |
| `chatBindings` | 群聊绑定 | chat_id → scope 映射，实现"群即边界" |
| `schedule` | 定时任务 | wiki-manager 每周一 8:30 自动同步；weekly-reporter 9:00 生成周报 |

### 2.3 从飞书消息到回答的完整链路

以下是一个真实请求的完整链路（"@司南 达人筛选标准是什么"）：

```
Step 1  用户在"垂类达人孵化项目群"发送消息
        └── 消息体：{text: "@司南 达人筛选标准是什么", chat_id: "oc_d2f8a9f..."}

Step 2  Gateway 接收消息，提取 chat_id
        └── OpenClaw Gateway 监听飞书机器人事件

Step 3  chatBindings 查找 scope
        └── oc_d2f8a9f659fce3626572c2bd80083d23 → scope = "kol-incubation"
        └── 将 scope 作为上下文参数附加到请求

Step 4  Gateway 转发到 qa-bot（entryPoint）
        └── qa-bot 的 workspace 是当前工作目录（CWD）

Step 5  qa-bot 的 intent skill 识别意图
        ├── 关键词匹配："筛选标准"、"SOP" → 知识查询
        ├── 置信度：0.95
        └── 输出：{intent: "knowledge_query", target_skill: "query", scope: "kol-incubation"}

Step 6  qa-bot 的 query skill 调用 wiki_query.py
        ├── 传入参数：question="达人筛选标准是什么", scope="kol-incubation"
        ├── wiki_query.py 读取 workspace/knowledge/wiki/index.md 了解知识库全貌
        ├── 按关键词"达人筛选"匹配相关页面
        ├── 按 scope 过滤：只读 public/ + dept/ + projects/kol-incubation/ + entities/ + concepts/
        ├── 模糊匹配默认优先检索当前 scope（kol-incubation）的文档
        └── 检索到：projects/kol-incubation/达人筛选标准.md

Step 7  wiki_query.py 返回结构化结果
        ├── context: "三维度评分模型：基础素质 40%、内容潜力 35%、商业潜力 25%..."
        ├── source: "[[达人筛选标准]]"
        └── lark_url: "https://ncnkdep1f4r7.feishu.cn/wiki/..."

Step 8  qa-bot 调用 LLM 润色生成自然语言回答
        ├── LLM 接收：context + source + lark_url + question
        ├── 基于 SKILL.md 中的输出模板生成回答
        └── 红线检查：无思考过程、无本地路径、只输出一条消息

Step 9  Gateway 将回答推送到飞书群聊
        └── Markdown 格式，包含 [[PageName]] 引用和飞书原文链接

Step 10 用户看到回复（只一条消息）
        ├── "垂类达人孵化的达人筛选采用三维度评分模型..."
        ├── "来源：[[达人筛选标准]]"
        └── "飞书原文：[达人筛选标准](https://ncnkdep1f4r7.feishu.cn/wiki/...)"
```

**整条链路耗时**：< 3 秒（本地工具查询）+ LLM 生成时间。

### 2.4 4 个 Agent 的详细职责

#### qa-bot（入口 Agent / 调度中心）

```json
{
  "entryPoint": true,
  "skills": ["intent", "query", "data-query", "route", "graph-query"],
  "delegatesTo": ["wiki-manager", "weekly-reporter", "card-builder"],
  "chatBindings": {
    "oc_d2f8a9f659...": { "name": "垂类达人孵化项目群", "scope": "kol-incubation" },
    "oc_b4225b78e6...": { "name": "品牌代运营项目群", "scope": "brand-ops" }
    // ... 共 5 个群聊绑定
  }
}
```

**核心职责**：
- **意图识别**：所有用户输入先过 intent skill，分类为知识查询/数据查询/图谱查询/操作请求/闲聊
- **查询执行**：知识类调用 query skill → wiki_query.py；数据类调用 data-query skill → data_query.py；图谱类调用 graph-query skill → graph_query.py
- **Agent 调度**：操作类请求（刷新知识库、生成周报、发通知）通过 route skill 调用对应 Agent
- **上下文感知**：根据 chatBindings 自动绑定 scope，实现"你在哪个群，就只能查哪个项目"
- **红线守卫**：通过 systemPrompt + SKILL.md 强制约束输出格式

**不做什么**：
- 不直接操作飞书 API（由 wiki-manager 负责）
- 不直接渲染卡片（由 card-builder 负责）
- 不直接生成周报（由 weekly-reporter 负责）

#### wiki-manager（知识同步 Agent）

```json
{
  "canBeCalledBy": ["qa-bot"],
  "skills": ["lark-api", "wiki-sync", "base-sync", "wiki-ingest", "wiki-graph"],
  "schedule": {
    "full_sync": "30 8 * * 1",      // 每周一 8:30 全量同步
    "incremental_check": "0 */6 * * *" // 每 6 小时增量检查
  }
}
```

**核心职责**：维护知识底座的新鲜度。不是回答问题的 Agent，而是"图书管理员"——负责从飞书拉取内容、整理、编译、构建图谱，供 qa-bot 消费。

**完整同步链路（4 步流水线）**：

```
Step 1: wiki-sync（Wiki 文档拉取）
    ├── 读取 config/sources.yaml 获取同步源配置
    ├── 对比 sync_state.json 中记录的 content_hash（sha256）
    ├── 检测到变更的文件 → 通过 lark-cli docs +fetch 拉取
    ├── 保存原始镜像到 raw_lark/wiki/<scope>/
    └── 输出：changed_files, sync_report

Step 2: base-sync（Base 数据拉取）
    ├── 读取 schema/*.yaml 注册表（定义各项目的 Base 表结构）
    ├── 对比 sync_state.json 中记录的 content_hash
    ├── 检测到变更的表格 → 通过 lark-cli base +record-list 拉取
    ├── 规范化处理：展平嵌套字段、统一日期格式、空值处理
    ├── 保存到 workspace/knowledge/data/<项目>/<table>.json
    └── 输出：changed_tables, sync_report

Step 3: wiki-ingest（知识编译）
    ├── 读取 prompts/ingest.md 获取编译规范
    ├── 对每篇变更文档执行 LLM 深度理解
    ├── 生成 Source Page（含 Summary / Key Claims / Key Quotes / 实体引用 / 概念引用）
    ├── 更新 workspace/knowledge/wiki/index.md（知识库索引）
    ├── 更新 workspace/knowledge/wiki/overview.md（全局概览）
    ├── 创建/更新 Entity Pages（workspace/knowledge/wiki/entities/{Name}.md）
    ├── 创建/更新 Concept Pages（workspace/knowledge/wiki/concepts/{Name}.md）
    ├── 检测文档间矛盾（同一实体在不同文档中的描述冲突）
    ├── 追加 workspace/knowledge/wiki/log.md（同步日志）
    └── 输出：ingested_pages, log

Step 4: graph-build（知识图谱构建）
    ├── 调用 build_graph.py
    ├── 从编译后的 wiki/ 目录提取节点（文档、实体、概念）和边（引用、关联）
    ├── 生成 workspace/knowledge/graph/graph.json（结构化图谱数据）
    ├── 生成 workspace/knowledge/graph/graph.html（vis.js 交互式可视化）
    └── 输出：graph.json, graph.html
```

**关键设计**：
- **增量同步**：通过 content_hash 判断变更，未变更的文件跳过，避免重复 LLM 调用
- **原始镜像保留**：raw_lark/ 保留飞书原文，workspace/knowledge/wiki/ 保留 LLM 编译后的结构化知识，两者物理隔离
- **数据与文档分离**：Base 数据不进入 Markdown 编译流程，直接保存为 JSON，供 data_query.py 读取
- **并发控制**：同步过程加锁（state/lock），防止多个任务同时执行导致数据损坏

#### weekly-reporter（周报生成 Agent）

```json
{
  "canBeCalledBy": ["qa-bot"],
  "delegatesTo": ["card-builder"],
  "schedule": { "weekly_report": "0 9 * * 1" },  // 每周一 9:00
  "triggers": ["生成周报", "部门看板", "周报汇总"]
}
```

**核心职责**：自动化周报生产。从 Base 采集上周数据，按场景配置合成项目周报和部门看板，再调用 card-builder 推送到飞书群。

**工作流程**：
1. **数据采集**：从 workspace/knowledge/data/ 读取各项目上周 KPI 快照
2. **趋势分析**：对比前一周数据，计算变化量、变化率
3. **周报生成**：按模板（metadata + 任务完成 + KPI + 风险 + 本周计划）生成 Markdown
4. **部门聚合**：汇总多个项目周报，生成部门看板（N 个项目状态 + Top3 知识精选）
5. **调用 card-builder**：将 Markdown 渲染为飞书消息卡片并推送

**为什么独立为一个 Agent？**
- 周报生成涉及大量数据聚合和 LLM 长文本生成，与实时问答的延迟要求不同（问答要秒级，周报可接受分钟级）
- 周报模板和场景配置经常变化，独立 Agent 可独立迭代
- 周报需要定时触发（cron），与事件驱动的 qa-bot 生命周期不同

#### card-builder（卡片渲染 Agent）

```json
{
  "canBeCalledBy": ["weekly-reporter"]
}
```

**核心职责**：将 Markdown/数据渲染为飞书消息卡片 JSON。是系统的"UI 层"。

**为什么独立为一个 Agent？**
- 飞书消息卡片有复杂的 JSON Schema，与业务逻辑解耦
- 一个 Agent 专注做"好看"，可以积累多种卡片模板（数据卡片、周报卡片、通知卡片）
- weekly-reporter 可以复用 card-builder，未来其他 Agent 也可以复用

### 2.5 Agent 间协作关系

```
┌─────────────────────────────────────────────────────────────┐
│                     飞书项目群（用户入口）                      │
│               @司南 提问 → Gateway → 分发                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │    qa-bot      │  ← entryPoint，所有流量入口
              │   （调度中心）  │
              └───────┬────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────────┐  ┌────────────┐
│ 查询类    │  │ 操作类        │  │ 闲聊/介绍   │
│自己处理   │  │委派给其他Agent│  │自己处理     │
└────┬─────┘  └──────┬───────┘  └────────────┘
     │               │
     ▼               ▼
  wiki_query    wiki-manager
  data_query    weekly-reporter
  graph_query   card-builder
```

**调度规则**：
- **查询类意图**（知识/数据/图谱/自我介绍/闲聊）：qa-bot **自己处理**，不转发
- **操作类意图**（刷新知识库/生成周报/推送卡片）：qa-bot 识别后调用 route skill，向用户确认"已触发 xxx 执行"，再调度对应 Agent
- **边界模糊时**：优先自己回答；确实需要其他 Agent 能力时再调度

### 2.6 Skill 与 Tool 的分层

Compass 采用 **"SKILL.md 定义接口，Python 工具实现逻辑"** 的分层设计：

| 层级 | 文件 | 作用 | 示例 |
|------|------|------|------|
| **Skill 定义** | `skills/<name>/SKILL.md` | 定义触发条件、查询链路、输出格式、红线 | data-query/SKILL.md 定义"何时触发、如何查询、输出模板" |
| **Skill 调用** | OpenClaw 运行时 | 根据意图匹配 Skill，加载 SKILL.md 作为 LLM 上下文 | intent skill 输出 "data_query" → 加载 data-query/SKILL.md |
| **工具实现** | `tools/<name>.py` | 精确的逻辑实现（文件 I/O、API 调用、数据过滤） | data_query.py 读取 JSON、过滤记录、计算统计 |
| **工具调用** | Python import | Skill 中通过 Python 代码直接调用工具函数 | `from tools.data_query import query_data` |

**qa-bot 的 5 个 Skill + 3 个工具**：

```
skills/
├── intent/       → 意图分类（关键词规则，无需工具）
├── query/        → 知识检索 → 调用 wiki_query.py
├── data-query/   → 数据查询 → 调用 data_query.py
├── graph-query/  → 图谱查询 → 调用 graph_query.py
└── route/        → Agent 调度 → 调用 OpenClaw Agent API

tools/
├── wiki_query.py   → 读取 wiki/ 目录，关键词匹配，scope 过滤
├── data_query.py   → 读取 data/ 目录，结构化过滤，聚合计算
└── graph_query.py  → 读取 graph.json，子图提取，HTML 生成
```

**为什么分层？**
- SKILL.md 给 LLM 看：定义"应该做什么"，作为 Prompt 的一部分
- Python 工具给机器执行：定义"怎么做"，精确、可测试、无幻觉
- LLM 负责"理解和生成"，Python 负责"精确执行"——各尽其责

### 2.7 Workspace 软链接设计

每个 Agent 有自己的 workspace 目录，作为 OpenClaw 运行时的 CWD（当前工作目录）：

```
agents/qa-bot/workspace/
├── AGENTS.md      → OpenClaw 运行时文件
├── IDENTITY.md    → 人格定义
├── skills/ -> ../skills           # 软链接：本 Agent 的技能
├── tools/ -> ../tools             # 软链接：本 Agent 的工具
├── data/ -> ../../workspace/knowledge/data    # 软链接：共享数据
├── graph/ -> ../../workspace/knowledge/graph  # 软链接：共享图谱
└── wiki/ -> ../../workspace/knowledge/wiki    # 软链接：共享知识
```

**为什么这样设计？**
1. **运行时 CWD 隔离**：每个 Agent 在自己的 workspace 内运行，路径相对，互不干扰
2. **全局资源共享**：wiki/data/graph 是所有 Agent 共享的，通过软链接挂载到各自 workspace
3. **职责分离**：代码/配置在 workspace 外（实际目录），运行时数据在 workspace 内
4. **OpenClaw 兼容**：OpenClaw 要求工具从 workspace 内访问，软链接满足这个约束

### 2.8 Scope 流转与权限检查机制

Scope 是 Compass 权限模型的核心。它不是传统的 RBAC（基于角色的访问控制），而是**基于群聊的上下文感知隔离**。

**流转链路**：

```
飞书消息
  └── chat_id: "oc_d2f8a9f659fce3626572c2bd80083d23"
      └── chatBindings 查找（qa-bot/agent.json）
          └── scope = "kol-incubation"
              └── 权限检查（systemPrompt 中定义）
                  └── 可访问范围：
                      ├── public/          → 公共知识（使用说明、流程规范）
                      ├── dept/            → 部门级知识（部门周报、项目汇总）
                      ├── projects/kol-incubation/  → 本项目知识（SOP、会议纪要）
                      ├── entities/        → 实体页（达人、客户、项目）
                      └── concepts/        → 概念页（SOP、策略、指标）
                  └── 不可访问范围：
                      ├── projects/brand-ops/       → ❌ 其他项目
                      ├── projects/live-commerce/   → ❌ 其他项目
                      └── ...
              └── 数据查询时
                  └── 只读取 workspace/knowledge/data/kol-incubation/
                  └── 不读取 workspace/knowledge/data/brand-ops/
```

**数据分级**：

| 信息类型 | 跨项目访问 | 原理 |
|----------|-----------|------|
| **公开信息**（PM 姓名、项目成员、项目状态） | ✅ 可回答 | 来自 dept/ 或 entities/，所有 scope 可读 |
| **敏感数据**（GMV、转化率、达人收入、客户满意度） | ❌ 拒答 | 来自 data/<项目>/，严格按 scope 隔离 |

**拒答不是 Prompt 层面的"请求 LLM 不要说"，而是物理层面的"工具层面就读不到数据"**——data_query.py 在读取前会检查 scope，跨项目数据直接不加载。

### 2.9 扩展性：如何新增一个 Agent？

Compass 的架构支持水平扩展。以新增"risk-monitor（风险监控 Agent）"为例：

```
Step 1: 新建目录结构
    agents/risk-monitor/
    ├── agent.json          → 定义 skills, canBeCalledBy, triggers
    ├── workspace/          → 运行时目录
    ├── skills/             → 风险识别、阈值检查等技能
    └── tools/              → 风险扫描脚本

Step 2: 写 agent.json
    {
      "canBeCalledBy": ["qa-bot"],
      "triggers": ["风险预警", "异常检测"],
      "skills": ["risk-scan", "threshold-check"]
    }

Step 3: 在 qa-bot 中注册
    ├── intent skill：增加 "风险监控" 意图类别
    ├── route skill：增加 risk-monitor → risk-monitor 的映射
    └── agent.json delegatesTo：加入 "risk-monitor"

Step 4: 无需修改 qa-bot 的核心问答逻辑
    qa-bot 的 query/data-query/graph-query 完全不受影响
```

**新增 Skill 同理**：在 qa-bot 的 skills/ 目录下新建 `risk-assess/SKILL.md` 和 `tools/risk_assess.py`，无需改动其他 Skill。

### 2.10 知识底座三层结构

```
┌──────────────────────────────────────────┐
│              应用层（qa-bot）              │
│    意图识别 → 路由分发 → 回答生成          │
│         （OpenClaw + LLM 推理）           │
└──────────────────┬───────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ 文档层  │ │ 数据层  │ │ 图谱层  │
   │Wiki知识 │ │Base数据 │ │关系网络 │
   │(RAG检索)│ │(结构化) │ │(可视化) │
   └────────┘ └────────┘ └────────┘
   非结构化    结构化      图结构
   适合SOP/    适合KPI/    适合关系
   会议纪要    档案/记录    发现/可视
```

- **文档层**：wiki_query.py 基于关键词/向量检索，适合非结构化知识（SOP、会议纪要、方法论）
- **数据层**：data_query.py 基于 JSON 结构化过滤，适合精确数值查询（KPI、档案、记录）
- **图谱层**：graph_query.py 基于图遍历，适合关系发现（"某达人在哪些会议中被提及"、"某概念出现在哪些文档中"）

三层互补，覆盖 90%+ 的业务问答场景。

---

## 三、核心创新亮点

### 亮点 1：Scope-Aware 权限隔离（不是简单的 RBAC）

**传统做法**：用户登录后根据角色判断权限（管理员/成员/访客）。

**Compass 做法**：**根据聊天群自动推断 scope**，用户甚至不用登录。你在"垂类达人孵化项目群"提问，系统默认只查该项目数据；你在"品牌代运营项目群"，看到的答案完全不同。

**更精细的是数据分级**：

| 信息类型 | 跨项目访问 | 示例 |
|----------|-----------|------|
| **公开信息** | ✅ 可回答 | "直播电商的 PM 是谁？" → "郑十三" |
| **敏感数据** | ❌ 拒答 | "直播电商上周 GMV 多少？" → ⚠️ 跨项目敏感数据未开放 |

公开信息（PM 姓名、项目成员、项目状态）可以跨项目回答；敏感 KPI（GMV、转化率、达人收入、客户满意度）严格按 scope 隔离。

### 亮点 2：模糊匹配 + 默认本项目

用户不需要记忆任何指令格式：

| 用户提问 | 系统行为 |
|----------|----------|
| "本周达人周均变现多少？" | 自动识别当前 scope，返回 kol-incubation Week 9 数据 |
| "达人筛选标准是什么？" | 自动检索 kol-incubation 的 SOP 文档 |
| "看看本周数据" | 返回当前项目最新周度 KPI 汇总 |

**无需指定项目名称，无需记忆达人编号**，像和同事聊天一样自然。

### 亮点 3：数据查询 → 文档查询的自动降级

当用户问的数据不在 Base 中（比如问了 Week 20，但最新只有 Week 9），系统：

1. **不编造、不外推**
2. **自动降级为文档查询**，检索相关 SOP、项目文档、数据说明
3. 返回文档链接，告知最新数据时间范围

```markdown
根据现有资料，垂类达人孵化项目暂无 Week 20 的数据。当前最新数据为 Week 9（2026-04-27 至 2026-05-03）。

以下相关文档可能对您有帮助：
- [[垂类达人孵化项目周报]] — 项目数据说明与更新节奏
- [[达人数据看板使用指南]] — 数据查询范围与时间覆盖说明
```

这是"Honest AI"的体现——**承认不知道，但给方向**。

### 亮点 4：交互式知识图谱子图

用户问"看看垂类达人孵化的知识图谱"，系统：

1. 从全量图谱中提取"垂类达人孵化"相关子图（含 1 跳邻居）
2. 生成可交互的 vis.js HTML 页面
3. 返回 Markdown 链接，点击即可查看

```markdown
**"垂类达人孵化" 子图搜索结果**：
- 直接匹配节点数：2
- 子图总节点数：53（含 1 跳邻居）
- 子图边数：194

**交互式子图**：
- 📎 [查看垂类达人孵化子图](http://localhost:8766/subgraph_垂类达人孵化.html)
```

不是静态截图，是**可拖拽、可缩放、可点击查看节点详情的交互式网络图**。

### 亮点 5：严格的输出约束（Red Lines）

通过 SKILL.md 中的强制规则，确保 LLM 输出"像人话"：

| 红线 | 说明 |
|------|------|
| **严禁输出思考过程** | 不展示"让我查一下"、"根据数据分析"等中间状态 |
| **严禁暴露本地路径** | 不暴露 `workspace/`、`*.json` 等本地路径 |
| **严禁暴露检索过程** | 不说"扫描文件"、"读取 JSON"、"过滤记录" |
| **只输出一条消息** | 最终答案本身，禁止分条发送 |
| **数据来源必须可溯源** | 必须附带飞书 Wiki/Base 原文链接 |

---

## 四、AI 技术深度解析

### 4.1 高阶 AI 技巧

**1. 意图分类 + 路由分发（非端到端生成）**

不是所有问题都丢给 LLM 生成答案。先由 intent skill 分类：

```
用户提问
    ├── 自我介绍 → 直接返回模板（无需 LLM）
    ├── 文档查询 → wiki_query.py（RAG 检索）→ LLM 润色
    ├── 数据查询 → data_query.py（结构化过滤）→ LLM 生成表格
    ├── 图谱查询 → graph_query.py（子图提取）→ 返回链接
    ├── 闲聊 → 礼貌拒答，引导回工作话题
    └── 跨项目敏感数据 → 标准拒答话术
```

**分层原则**：能规则不模型，能模型不端到端——降低幻觉，提升可控性。

**2. 结构化输出约束（Prompt 工程三层架构）**

| 层级 | 文件 | 作用 |
|------|------|------|
| 全局行为 | `systemPrompt` in agent.json | 定义 Agent 身份、能力边界、输出格式 |
| 人格层 | `IDENTITY.md` / `SOUL.md` | 定义语气、风格、emoji 使用 |
| 具体能力 | `SKILL.md`（每个 skill 一个） | 定义触发条件、查询链路、输出示例、红线 |

LLM 不是自由发挥，而是在**严格的结构化模板**中填空。

**3. RAG + 结构化查询的双轨检索**

- **文档层**：wiki_query.py 基于向量/关键词检索，适合非结构化知识（SOP、会议纪要）
- **数据层**：data_query.py 基于结构化过滤，适合精确数值查询（KPI、档案、记录）
- 两者互补，覆盖 90%+ 的业务问答场景

**4. 知识图谱增强**

将 Wiki 文档和 Base 数据构建为异构知识图谱（项目-文档-达人-指标-会议节点），支持：
- 全局关系可视化
- 关键词子图提取
- 隐性关联发现（如"某达人在哪些会议中被提及"）

### 4.2 人与 AI 的分工

| 人类负责 | AI 负责 |
|---------|---------|
| 知识库维护（Wiki/Base 内容更新） | 实时检索、智能匹配 |
| 权限策略制定（哪些数据敏感） | 自动执行 scope 检查 |
| 业务判断和决策 | 数据呈现、趋势分析、周报初稿 |
| 异常问题处理 | 常规问题 7×24 秒级响应 |
| 周报内容审核 | 数据汇总 + LLM 润色生成 |

**关键设计**：AI 不替代人做决策，而是把人从"找信息"的重复劳动中解放出来，让人专注于"用信息做判断"。

### 4.3 核心模型选型思路

```
┌──────────────────────────────────────────┐
│           OpenClaw（编排层）               │
│   任务分发 · 状态管理 · Agent 通信 · 工具调用 │
├──────────────────────────────────────────┤
│           LLM（推理层）                    │
│   意图识别 · 自然语言生成 · 回答润色         │
├──────────────────────────────────────────┤
│        Python 工具层（精确层）              │
│   数据过滤 · 图谱构建 · Base API · 文件 I/O  │
└──────────────────────────────────────────┘
```

- **OpenClaw**：轻量级 Agent 框架，支持 skill-based 调用链，适合中小团队快速落地
- **LLM**：负责"理解"和"生成"，不做精确计算
- **Python 工具**：负责"精确执行"，不依赖模型推理

---

## 五、Demo 场景与验证

### 演示脚本设计（9 个核心用例）

| 幕 | 场景 | 验证能力 |
|----|------|----------|
| **第一幕** | 垂类达人孵化项目群（自己项目） | 自我介绍、SOP 文档检索、KPI 数据查询、知识图谱、闲聊拒答 |
| **第二幕** | 品牌代运营项目群（切换 scope） | 群切换感知、同一问题不同答案 |
| **第三幕** | 跨项目公开信息 | PM 姓名查询（应回答） |
| **第四幕** | 跨项目敏感数据 | KPI 查询（应拒答）+ 数据查不到时降级为文档查询 |

### 关键验证点

- ✅ 未指定项目名称时，默认指向当前 scope
- ✅ 跨项目敏感数据严格拒答，不泄露 GMV/转化率/满意度
- ✅ 数据查不到时自动返回文档链接，不编造
- ✅ 只输出一条消息，无思考过程
- ✅ 所有数据来源可溯源（飞书 Wiki/Base 链接）

---

## 六、实际价值与效率提升

| 指标 | 提升 |
|------|------|
| 信息检索时间 | 从 5-15 分钟 → **10 秒** |
| 新人上手成本 | 从"翻遍 Wiki" → **@司南 直接问** |
| 跨项目数据泄露风险 | 从"依赖人判断" → **系统自动拦截** |
| 周报撰写时间 | 从半天 → **数据自动聚合 + LLM 润色** |
| 知识沉淀 | 从"散落在各处" → **统一知识底座 + 图谱关联** |

---

## 七、可复用性与推广价值

Compass 的架构不绑定 MCN 行业。任何具有以下特征的团队都可以复用：

- ✅ 多项目并行（3+ 个项目组）
- ✅ 文档 + 数据双轨知识（Wiki + 表格/数据库）
- ✅ 有权限隔离需求（项目间数据敏感）
- ✅ 群聊是主要协作入口（飞书/钉钉/企业微信）

**潜在应用场景**：律所（案件知识库）、咨询公司（项目交付物管理）、研发管理（多团队文档+指标）、医疗（科室知识+病例数据）。

---

## 八、技术栈与工程规范

| 层级 | 技术 |
|------|------|
| Agent 框架 | OpenClaw |
| 知识检索 | Python + 关键词/向量检索 |
| 数据查询 | Python + JSON 结构化过滤 |
| 知识图谱 | Python + vis.js（前端可视化） |
| 数据同步 | 飞书 Wiki API + Base API |
| 消息卡片 | 飞书消息卡片 JSON |
| 部署 | 本地 Gateway（可扩展为云端） |

**工程规范**：
- Skill 化开发：每个能力独立为 SKILL.md + 工具脚本，可插拔
- 配置即代码：agent.json 定义 Agent 行为，版本可控
- 软链接共享：workspace 内通过软链接实现多 Agent 资源共享

---

*Compass — 让知识触手可及，让数据有边界，让协作更高效。*
