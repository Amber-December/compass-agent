# Compass（司南）产品数据流与多 Agent 协作架构

## 一、架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          数据源层（飞书原生）                              │
├──────────────┬──────────────┬────────────────┬──────────────────────────┤
│  飞书 Base   │  飞书 Wiki   │   飞书妙记      │      项目群 IM           │
│  (结构化数据) │  (文档知识)   │   (会议语音)    │      (消息/文件)          │
├──────────────┼──────────────┼────────────────┼──────────────────────────┤
│ project_kpi  │ 项目 OnePage │  选品会/复盘会  │      群文件上传           │
│ task_list    │ 周报归档     │  客户对接会     │      @提及消息            │
│ kol_profile  │ 会议纪要     │  技术评审会     │      任务打卡             │
│ weekly_report│ 项目文档     │                │                          │
│ risk_log     │ 数据看板     │                │                          │
└──────────────┴──────────────┴────────────────┴──────────────────────────┘
         │              │               │                  │
         ▼              ▼               ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        采集层（data-collection）                         │
│  • 从 Base 拉取 KPI/任务/风险数据  →  data/raw/base_YYYYMMDD.json        │
│  • 从 Wiki 拉取文档列表和内容      →  data/raw/wiki_YYYYMMDD.json        │
│  • 从妙记拉取会议摘要              →  data/raw/minutes_YYYYMMDD.json     │
│  • 从群聊拉取消息/文件             →  data/raw/messages_YYYYMMDD.json    │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        知识底座层（wiki-manager）                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ wiki/sources/   │  │  entities/      │  │  concepts/      │         │
│  │ 原始文档 Markdown│  │  实体关系图谱    │  │  概念定义       │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                         │
│  职责：本地 Markdown ↔ 飞书 Wiki 双向同步 + 构建 LLM 可检索的知识底座      │
└─────────────────────────────────────────────────────────────────────────┘
         │                              │
         │ (weekly-reporter 读取)       │ (qa-bot 检索)
         ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Agent 协作层（6 个 Agent）                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │weekly-reporter│───▶│ risk-monitor │    │dept-aggregator│            │
│  │  周报合成     │嵌入 │  风险检测     │    │  部门聚合      │            │
│  └──────┬───────┘    └──────────────┘    └──────┬───────┘             │
│         │                                         │                     │
│         │ ① 生成项目周报 Markdown                  │ ② 聚合部门看板       │
│         │ ② 归档到 Wiki 周报目录                   │ ③ Top3 精选         │
│         │ ③ 更新 OnePage 本周进展                  │                     │
│         │ ④ 推送卡片到项目群                       │ ④ 推送卡片到部门群   │
│         ▼                                         ▼                     │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │              输出层（card-builder + lark-api）            │           │
│  │         飞书消息卡片  →  项目群 / 部门群 / @回复          │           │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │ wiki-manager  │    │   qa-bot     │    │efficiency-   │             │
│  │  知识库管理   │    │  自然查询     │    │  analyzer    │             │
│  │  (底座构建)   │    │  (@事件驱动)  │    │  效能分析     │             │
│  └──────────────┘    └──────────────┘    └──────────────┘             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、核心数据流详解

### 2.1 周一早晨主链路（定时触发）

**时间节点：每周一 9:00 → 9:05**

```
9:00 weekly-reporter 触发
    │
    ├─▶ data-collection 采集上周数据
    │       ├─ Base: project_kpi（上周 KPI 数值）
    │       ├─ Base: task_list（任务完成/延期状态）
    │       ├─ Wiki: 本周新增/修改的文档列表
    │       └─ 妙记: 上周会议摘要
    │
    ├─▶ 调用 risk-monitor 嵌入检测
    │       ├─ 扫描 KPI 连续下滑/越界
    │       ├─ 提取妙记/消息中的风险关键词
    │       └─ 输出：风险段落（🔴🟡🟢）
    │
    ├─▶ 按 prompts/mcn/weekly-report.md 生成
    │       └─ 项目周报 Markdown
    │
    ├─▶ 调用 wiki-manager 归档
    │       ├─ 在 Wiki「周报归档」下创建新节点
    │       ├─ 写入周报 Markdown 内容
    │       └─ 更新 OnePage 的"本周进展"和"核心 KPI"表格
    │
    └─▶ 调用 card-builder 推送
            └─ 飞书消息卡片 → 项目群

9:05 dept-aggregator 触发
    │
    ├─▶ 接收 weekly-reporter 产出的 6 个项目周报
    │
    ├─▶ 按 prompts/mcn/dept-aggregator.md 聚合
    │       ├─ 状态分布（🟢🟡🔴 计数）
    │       ├─ 部门 KPI 快照表
    │       └─ Top3 知识精选（评分排序）
    │
    └─▶ 调用 card-builder 推送
            └─ 部门看板卡片 → 部门群
```

### 2.2 问答链路（事件驱动）

```
项目群内用户 @司南 提问
    │
    ▼
qa-bot 接收消息
    │
    ├─▶ intent-classifier 识别意图
    │       ├─ 数据查询 → 查 Base 数据
    │       ├─ 知识查询 → 查本地 LLM-Wiki
    │       ├─ 跨项目查询 → 判断权限
    │       └─ 边界外推 → 拒答
    │
    ├─▶ 权限判断
    │       ├─ 本项目数据/知识 → 允许回答
    │       ├─ 部门级聚合/共享知识 → 允许回答
    │       └─ 其他项目敏感数据 → 拒答
    │
    ├─▶ 检索本地知识底座（wiki-manager 构建）
    │       ├─ wiki/sources/ 原始文档
    │       ├─ entities/ 实体关系
    │       └─ concepts/ 概念定义
    │
    └─▶ 生成带引用的 Markdown 答案
            ├─ 答案正文
            ├─ 来源引用（飞书文档链接）
            └─ 相关行动项（如有）
```

### 2.3 知识底座同步链路（定时/被动）

Compass 采用 **符号化知识编译（Symbolic Knowledge Compilation）** 构建知识底座，不依赖向量数据库。核心流程：

```
wiki-manager 定期同步
    │
    ├─▶ 增量拉取 Wiki 更新
    │       ├─ 读取新增/修改的 Wiki 文档
    │       └─ 保存到 workspace/raw_lark/
    │
    ├─▶ 知识编译（tools/wiki_ingest.py）
    │       ├─ 解析 Markdown，提取 frontmatter（含 lark_url）
    │       ├─ 生成结构化来源页 → wiki/sources/<slug>.md
    │       ├─ 提取实体（达人、品牌、项目）→ wiki/entities/<Name>.md
    │       ├─ 提取概念（SOP、规范、方法论）→ wiki/concepts/<Name>.md
    │       ├─ 自动创建 [[Wikilink]] 交叉引用
    │       ├─ 更新 wiki/index.md 索引
    │       └─ 更新 wiki/overview.md 全局综合
    │
    ├─▶ 构建知识图谱（tools/build_graph.py）
    │       ├─ Pass 1: 提取显式 [[Wikilink]] → EXTRACTED 边
    │       ├─ Pass 2: LLM 语义推断隐式关系 → INFERRED/AMBIGUOUS 边
    │       ├─ Louvain 社区检测（自动聚类主题）
    │       └─ 输出 graph/graph.json + graph/graph.html
    │
    └─▶ 检索就绪
            ├─ 索引：wiki/index.md（关键词匹配入口）
            ├─ 图谱：graph/graph.json（邻居扩展）
            └─ 内容：wiki/sources/ + entities/ + concepts/

【人工操作也会触发同步】
PM 在飞书 Wiki 修改 OnePage
    │
    ▼
下次 wiki-manager 同步时
    │
    ├─▶ 拉取变更 → workspace/raw_lark/
    ├─▶ wiki_ingest.py 重新编译（SHA256 缓存增量更新）
    └─▶ build_graph.py 增量更新图谱
```

**检索机制（qa-bot 调用）**：

```
用户提问
    │
    ▼
tools/wiki_query.py
    │
    ├─▶ Step 1: 关键词匹配 wiki/index.md
    │       └─ CJK 双字滑动窗口 + 项目范围过滤
    │
    ├─▶ Step 2: 图邻居扩展（graph/graph.json）
    │       └─ 置信度 ≥ 0.7 的 INFERRED 边参与扩展
    │
    ├─▶ Step 3: 读取相关页面完整内容
    │       └─ 优先返回 overview.md
    │
    ├─▶ Step 4: LLM 综合答案
    │       └─ 要求标注 [[PageName]] 来源引用
    │
    └─▶ Step 5: 返回带飞书链接的 Markdown 答案
            └─ sources[].lark_url 指向原始飞书文档
```

---

## 三、四大文档的维护关系

### 3.1 项目 OnePage（动态更新 + 静态信息）

```
┌─────────────────────────────────────────────────────┐
│ 项目 OnePage                                        │
├─────────────────────────────────────────────────────┤
│ 基本信息（静态）                                    │
│   • 项目名称、目标、PM、成员、启动时间              │
│   → PM 手动维护，长期不变                           │
├─────────────────────────────────────────────────────┤
│ 核心 KPI（动态）                                    │
│   • 表格：指标 | 目标值 | Week N 当前值 | 状态      │
│   → weekly-reporter 每周一自动更新 "当前值" 和 "状态" │
├─────────────────────────────────────────────────────┤
│ 本周进展（动态）                                    │
│   • 已完成 / 进行中 / 阻塞风险                      │
│   → weekly-reporter 每周一自动更新                  │
├─────────────────────────────────────────────────────┤
│ 历史趋势（半动态）                                  │
│   • 各周数据表格                                    │
│   → weekly-reporter 每周追加一行新数据              │
├─────────────────────────────────────────────────────┤
│ 资源需求（静态）                                    │
│   • 预算、人力、外部合作                            │
│   → PM 手动维护，有变化时更新                       │
└─────────────────────────────────────────────────────┘
```

**关键机制**：OnePage 不是孤立的总结文档，而是 weekly-reporter 的**输出靶点**——周报生成后，weekly-reporter 会反向将核心数据写回 OnePage，确保它始终是项目的最新快照。

### 3.2 周报（自动生成 + 归档）

```
生成流程：
    Base 数据 ──┐
    妙记摘要 ────┼─▶ weekly-reporter ──▶ 周报 Markdown
    Wiki 更新 ───┤         │
    风险检测 ────┘         │
                           ├─▶ 归档到 Wiki「周报归档」目录
                           │       （创建新节点，命名：[日期范围] Week N 周报）
                           │
                           ├─▶ 更新项目 OnePage
                           │       （核心 KPI 表格 + 本周进展）
                           │
                           └─▶ 推送飞书卡片到项目群
                                   （摘要版，含"查看完整周报"按钮）
```

**双轨制**：
- **飞书 Wiki 中的周报** = 完整版，可供随时查阅、历史追溯、被 qa-bot 检索
- **项目群卡片** = 摘要版，一屏读完，引导点击跳转完整文档

### 3.3 会议纪要（人工维护 + AI 提取）

```
实际开会 → 飞书视频会议 → 自动生成妙记
    │
    ├─▶ 人工整理会议纪要 Markdown
    │       → 保存到本地 docs/projects/{项目}/会议纪要/
    │       → 推送/更新到 Wiki「会议纪要」目录
    │
    └─▶ weekly-reporter 每周采集
            ├─ 读取妙记 AI 摘要（议题/决策/待办）
            ├─ 提取关键决策和 TODO
            └─ 嵌入到当周周报的"本周关键动态"部分
```

**维护责任**：
- **人工**：确保 Wiki 中的会议纪要文档结构完整、信息准确
- **AI**：weekly-reporter 自动提取要点，减少 PM 手动汇总工作量

### 3.4 数据看板（Base 驱动 + 可视化）

```
飞书 Base（project_kpi 表）
    │
    ├─▶ 飞书 Base 原生视图（表格/仪表盘）
    │       → PM 日常查看、数据录入
    │
    └─▶ data-collection 拉取
            │
            ├─▶ weekly-reporter 生成周报中的"数据看板"表格
            │
            ├─▶ risk-monitor 扫描阈值触发预警
            │
            └─▶ efficiency-analyzer 生成趋势洞察
```

**Base 表设计**：

| 表名 | 用途 | 与 Agent 的关系 |
|------|------|----------------|
| `project_kpi` | 存储各项目每周 KPI 数值 | weekly-reporter 读取生成数据看板；risk-monitor 扫描阈值 |
| `task_list` | 存储项目任务及完成状态 | weekly-reporter 读取生成任务完成情况 |
| `kol_profile` | 达人档案信息 | qa-bot 回答达人相关查询 |
| `weekly_report` | 周报元数据（生成时间、状态、归档位置） | weekly-reporter 写入归档记录 |
| `risk_log` | 风险记录与处理状态 | risk-monitor 写入检测记录；weekly-reporter 读取生成风险段落 |

---

## 四、Agent 间调用关系矩阵

| 调用方 ↓ / 被调用方 → | wiki-manager | weekly-reporter | risk-monitor | dept-aggregator | qa-bot | efficiency-analyzer |
|----------------------|-------------|-----------------|--------------|-----------------|--------|---------------------|
| **wiki-manager** | — | 提供知识底座 | — | 提供知识底座 | 提供知识底座 | — |
| **weekly-reporter** | 归档周报/更新 OnePage | — | 嵌入调用检测风险 | 输出周报供聚合 | — | — |
| **risk-monitor** | — | 被嵌入调用 | — | — | — | — |
| **dept-aggregator** | — | 读取各项目周报 | — | — | — | — |
| **qa-bot** | 检索知识底座 | — | — | — | — | — |
| **efficiency-analyzer** | — | — | — | — | — | — |

**说明**：
- `weekly-reporter → wiki-manager`：单向写入（归档 + 更新）
- `wiki-manager → qa-bot`：单向提供（知识底座检索）
- `weekly-reporter → risk-monitor`：嵌入调用（生成周报时同步检测风险）
- `weekly-reporter → dept-aggregator`：单向输出（周报作为部门聚合的输入）
- `qa-bot` 和 `efficiency-analyzer` 相对独立，不直接调用其他 Agent

---

## 五、数据闭环设计

### 5.1 周一主循环（周级闭环）

```
Base 数据录入（PM 日常维护）
    ↓
weekly-reporter 周一 9:00 读取 → 生成周报
    ↓
    ├─▶ 写入 Wiki 周报归档（知识沉淀）
    ├─▶ 更新 OnePage（项目快照）
    ├─▶ 推送项目群（即时触达）
    └─▶ 输出给 dept-aggregator
            ↓
            生成部门看板 → 推送部门群
    ↓
wiki-manager 定期同步 → 更新本地 LLM-Wiki
    ↓
qa-bot 基于最新知识底座回答群内问题
```

### 5.2 问答反哺（日常闭环）

```
qa-bot 被 @ 提问
    ↓
检索知识底座发现信息缺失/过时
    ↓
反馈给 wiki-manager（标记待更新）
    ↓
PM 补充/更新 Wiki 文档
    ↓
wiki-manager 同步到知识底座
    ↓
下次 qa-bot 回答更准确
```

### 5.3 风险跟踪（持续闭环）

```
risk-monitor 检测到风险
    ↓
weekly-reporter 将风险嵌入周报
    ↓
PM 在周会中讨论并形成会议纪要
    ↓
会议纪要中产生新的行动项（写入 task_list）
    ↓
下周 weekly-reporter 检查行动项完成状态
    ↓
风险解除或升级
```

---

## 六、文件与配置映射

| 组件 | 配置文件 | Prompt 模板 | 脚本/工具 |
|------|---------|-------------|----------|
| 场景定义 | `config/scenarios/mcn.yaml` | — | — |
| weekly-reporter | `openclaw.json` (agent 配置) | `prompts/mcn/weekly-report.md` | `scripts/generate_kol_project_docs.py` |
| risk-monitor | `config/scenarios/mcn.yaml` (thresholds) | `prompts/mcn/risk-monitor.md` | — |
| dept-aggregator | `openclaw.json` (agent 配置) | `prompts/mcn/dept-aggregator.md` | — |
| qa-bot | `openclaw.json` (agent 配置) | `prompts/mcn/qa-bot.md` | — |
| wiki-manager | `.env` (WIKI_SPACE_ID) | `agents/wiki-manager/prompts/wiki-push-guide.md` | `scripts/push_kol_wiki.py` |
| data-collection | — | — | `shared/skills/data-collection/SKILL.md` |
| card-builder | — | — | `shared/skills/card-builder/SKILL.md` |

---

## 七、当前状态与下一步

### 已就绪
- [x] 飞书 Wiki 知识库结构（6 大一级目录 + 项目二级目录）
- [x] 垂类达人孵化项目完整文档（23 篇）
- [x] 其余 5 个项目 OnePage + 项目列表看板
- [x] 4 个 Agent 的 Prompt 模板
- [x] Base Mock 数据（KPI × 9 周 + 任务列表 + Q&A 评测集）
- [x] 共享 Skills 定义（data-collection / lark-api / card-builder）

### 待实现
- [ ] `tools/lark_ingest.py`：飞书 → 本地的数据拉取与适配层（P2 负责）
- [ ] `lark-event` 长连接框架：接收群 @ 消息触发 qa-bot（P2 负责）
- [ ] 飞书 Base 真实表创建与数据录入（可用 Mock 数据作为初始值）
- [ ] 周报生成自动化脚本（打通 data-collection → LLM → wiki-manager → card-builder 链路）

### 已就绪（本次新增）
- [x] `tools/wiki_ingest.py`：符号化知识编译（Markdown → 结构化 wiki/sources/ + entities/ + concepts/）
- [x] `tools/wiki_query.py`：图增强检索（关键词匹配 + graph.json 邻居扩展 → 带飞书链接引用的答案）
- [x] `tools/build_graph.py`：知识图谱构建（两-pass 建图 + Louvain 社区检测 + 交互式可视化）
- [x] `wiki/` 目录结构（index.md / overview.md / log.md / sources/ / entities/ / concepts/ / syntheses/）
- [x] 本地 LLM-Wiki 符号化底座（替代向量库方案，零外部依赖）

---

*文档版本：v1.0 | 维护：P1 业务场景设计 | 更新日期：2026-05-01*
