---
name: wiki-ingest
description: "Compass Ingest Prompt — 知识编译指令"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 适配 OpenClaw Agent 运行时。你作为 wiki-manager，将飞书拉取的原始 Markdown 编译为结构化知识底座。

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/wiki-ingest/`
- **执行脚本**: `tools/wiki_ingest.py`（单文件处理）、`tools/wiki_ingest_batch.py`（批量处理）

## 输入来源

`raw_lark/wiki/`（agent workspace 下的相对路径）下的 Markdown 文件，由 `wiki_sync.py` 从飞书 Wiki 拉取。每个文件已有**来源元数据 frontmatter**（仅含来源属性，不含 wiki 运行时状态）：

```yaml
---
title: "文档标题"
doc_type: project-weekly | meeting | project-doc | project-onepage | dept-weekly | dept-onepage | default
scope: public | dept | projects
project_id: "xxx"        # 仅 projects scope
lark_url: "https://..."
lark_node_id: "..."
content_hash: "sha256..."
fetched_at: "..."
status: active | archived
---
```

**你的职责**：读取这些原始文件，提取知识，写入 `workspace/knowledge/wiki/` 目录（项目根目录下的共享知识目录）。原始文件只读不写。

---

## Ingest 步骤（必须按顺序执行）

### Step 0 — 增量判断（前置过滤）

1. 读取源文件的 frontmatter，提取 `content_hash`。
2. 检查目标路径 `workspace/knowledge/wiki/{scope}/sources/{slug}.md` 是否已存在。
3. 如果存在，读取其 frontmatter 中的 `content_hash`：
   - 若 hash 相同 → **跳过该文件**，打印 "Content unchanged, skipping"。
   - 若 hash 不同 → 继续执行，revision + 1。
4. 如果 `status: archived` → 跳过（sync 阶段已处理归档）。

---

### Step 1 — 读取上下文

- 读取 `workspace/knowledge/wiki/index.md` —— 了解当前知识库全貌。
- 读取 `workspace/knowledge/wiki/overview.md` —— 了解当前综合认知。

---

### Step 2 — 读取源文档并判定文档类型

用 Read 工具完整读取源文件内容（含 frontmatter）。区分 frontmatter（元数据）和 body（正文）。

**文档类型判定优先级**（从高到低）：

1. **frontmatter `doc_type` 字段** — 首选。`wiki_sync.py` 在同步阶段已自动判定并写入。
2. **路径关键字** — 次选。如 `/周报归档/`、`/会议纪要/`、`/项目文档/`。
3. **标题 + 正文结构匹配** — 兜底。仅当无 `doc_type` 时触发。

| 类型标识 | 判定规则 | 典型路径/标题特征 |
|---------|---------|-----------------|
| `project-weekly` | 标题含"周报" + 正文含"数据看板""任务完成情况""风险与阻塞" | `垂类达人孵化/周报归档/` |
| `meeting` | 标题含"会议纪要"或"会议" + 正文含"基本信息""讨论要点""行动项" | `垂类达人孵化/会议纪要/` |
| `project-doc` | 标题含"手册""SOP""规范""方案""报告" + 正文含结构化流程/表格/Q&A | `垂类达人孵化/项目文档/` |
| `project-onepage` | 标题含"OnePage"或"项目 OnePage" + 正文含"核心KPI""风险阈值" | `*/项目 OnePage.md` |
| `dept-weekly` | 标题含"部门周报"或"[MCN事业部] 周报" + 正文含"项目数据速览" | `部门项目汇总/部门周报归档/` |
| `dept-onepage` | 标题含"部门 OnePage" + 正文含"项目概况" | `部门项目汇总/部门 OnePage.md` |
| `default` | 以上均不匹配 | — |

判定后，使用下方对应的**文档类型专用模板**生成 Source Page。严禁使用通用模板处理 `project-weekly`、`meeting` 等结构化文档。

---

### Step 3 — 生成 Source Page（Additive Only）

写入 `workspace/knowledge/wiki/{scope}/sources/{slug}.md`。slug 规则：
- 从源文件标题生成 `kebab-case`
- 中文标题用拼音或保留汉字（kebab-case 连接），如 `达人筛选标准` → `da-ren-shai-xuan-biao-zhun` 或 `达人筛选标准`（优先保留语义）

**核心原则：Additive Only（只增不减）**

由于 `wiki_sync.py` 已在同步阶段完成所有格式清洗（`lark-table` → markdown table、移除冗余脚注），raw_lark 的正文已经是**干净、可直接复用**的 markdown。ingest 阶段**禁止重写或修改正文**，只能：

1. **在正文前 prepend**：`状态概览`（如适用）
2. **在正文后 append**：`实体引用` + `概念引用` + `跨周关联`（如适用）+ `Contradictions`

正文本身必须**逐字保留**，包括：
- 所有表格（不得省略任何行/列）
- 所有列表
- 所有 Q&A
- 所有链接

**Source Page frontmatter = 来源元数据 + wiki 运行时元数据**：

```yaml
---
# 来源元数据（从 raw_lark frontmatter 透传）
title: "..."
doc_type: "..."
scope: "..."
project_id: "..."
lark_url: "..."
lark_node_id: "..."
content_hash: "..."
status: active
# wiki 运行时元数据（由 ingest 生成）
type: source
tags: []
date: YYYY-MM-DD
source_file: "raw_lark/wiki/.../文件名.md"  # 相对 agent workspace 的路径
revision: 1
last_synced_at: YYYY-MM-DDTHH:MM:SSZ
sources: []
---
```

---

## 文档类型专用模板

### 模板 1：项目周报 (project-weekly)

适用于项目层级周报，如 `垂类达人孵化/周报归档/` 下的文件。

```markdown
---
# 来源元数据（透传）
title: "<原文标题>"
doc_type: project-weekly
scope: "public" | "dept" | "projects"
project_id: "..."
lark_url: "https://..."
lark_node_id: "..."
content_hash: "..."
status: active
# wiki 运行时（ingest 生成）
type: source
tags: [project-weekly]
date: YYYY-MM-DD
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
source_file: "raw_lark/wiki/.../文件名.md"  # 相对 agent workspace 的路径
revision: 1
last_synced_at: YYYY-MM-DDTHH:MM:SSZ
sources: []
---

## [以下正文逐字保留 raw_lark 原文，不得修改]

## 1. 本周数据看板
> 原文表格已保留。

| 指标 | 本周 | 上周 | 环比 | 目标 | 状态 |
|------|------|------|------|------|------|
| ... | ... | ... | ... | ... | ... |

## 2. 任务完成情况
- ✅ 已完成：...
- ⏳ 进行中：...

## 3. 风险与阻塞
...

## 4. 下周计划
...

## 5. 相关链接
- [项目 OnePage](../项目 OnePage.md)
- ...

## [以上正文逐字保留 raw_lark 原文，不得修改]

## 实体引用
- [[实体名]] — 类型: project/brand/kol/person/platform/tool | 关系说明

## 概念引用
- [[概念名]] — 类型: SOP/strategy/metric/tool/workflow | 关系说明

## 跨周关联
- 上周周报：[[<项目名> <上周周期> 周报]]（如存在）
- 关联 OnePage：[[项目 OnePage]]

## Contradictions
- 与 [[另一页面]] 的矛盾点：...
```

---

### 模板 2：会议纪要 (meeting)

适用于会议纪要和同步会记录，如 `*/会议纪要/` 下的文件。

```markdown
---
# 来源元数据（透传）
title: "<原文标题>"
doc_type: meeting
scope: "public" | "dept" | "projects"
project_id: "..."
lark_url: "https://..."
lark_node_id: "..."
content_hash: "..."
status: active
# wiki 运行时（ingest 生成）
type: source
tags: [meeting]
date: YYYY-MM-DD
source_file: "raw_lark/wiki/.../文件名.md"  # 相对 agent workspace 的路径
revision: 1
last_synced_at: YYYY-MM-DDTHH:MM:SSZ
sources: []
---

## [以下正文逐字保留 raw_lark 原文，不得修改]

## 基本信息
- **会议主题**：...
- **会议时间**：...
- **参会人员**：[[李小明]]、[[张三]] ...
- **记录人**：[[...]]
- **会议类型**：...

## 会议议程
1. ...
2. ...

## 讨论要点
### 议题：...
- **背景**：...
- **关键结论**：...

## 决策与结论
1. ...
2. ...

## 行动项（TODO）
| 序号 | 事项 | 负责人 | 截止日期 | 优先级 | 状态 |
|------|------|--------|----------|--------|------|
| ... | ... | ... | ... | ... | ... |

## 风险提示
...

## 下次会议
- **时间**：...
- **主题**：...

## [以上正文逐字保留 raw_lark 原文，不得修改]

## 实体引用
- [[实体名]] — 类型: project/brand/kol/person/platform/tool | 关系说明

## 概念引用
- [[概念名]] — 类型: SOP/strategy/metric/tool/workflow | 关系说明

## Contradictions
- 与 [[另一页面]] 的矛盾点：...
```

---

### 模板 3：项目文档 (project-doc)

适用于 SOP、手册、规范、方案、报告等结构化文档，如 `*/项目文档/` 下的文件。

```markdown
---
# 来源元数据（透传）
title: "<原文标题>"
doc_type: project-doc
scope: "public" | "dept" | "projects"
project_id: "..."
lark_url: "https://..."
lark_node_id: "..."
content_hash: "..."
status: active
# wiki 运行时（ingest 生成）
type: source
tags: [project-doc]
date: YYYY-MM-DD
source_file: "raw_lark/wiki/.../文件名.md"  # 相对 agent workspace 的路径
revision: 1
last_synced_at: YYYY-MM-DDTHH:MM:SSZ
sources: []
---

## [以下正文逐字保留 raw_lark 原文，不得修改]

## 输出背景
- **来源会议**：...
- **关联决策**：...
- **使用场景**：...

## 一、合作模式（示例）
| 模式 | 说明 | 分成比例 | 适用对象 |
|------|------|----------|----------|
| ... | ... | ... | ... |

## 二、达人权益（示例）
- ...

## 三、常见问题（Q&A）
**Q：...？**
A：...

## [以上正文逐字保留 raw_lark 原文，不得修改]

## 实体引用
- [[实体名]] — 类型: project/brand/kol/person/platform/tool | 关系说明

## 概念引用
- [[概念名]] — 类型: SOP/strategy/metric/tool/workflow | 关系说明

## Contradictions
- 与 [[另一页面]] 的矛盾点：...
```

---

### 模板 4：项目 OnePage (project-onepage)

适用于项目总览页，如 `*/项目 OnePage.md`。

```markdown
---
# 来源元数据（透传）
title: "<原文标题>"
doc_type: project-onepage
scope: "public" | "dept" | "projects"
project_id: "..."
lark_url: "https://..."
lark_node_id: "..."
content_hash: "..."
status: active
# wiki 运行时（ingest 生成）
type: source
tags: [project-onepage]
date: YYYY-MM-DD
source_file: "raw_lark/wiki/.../文件名.md"  # 相对 agent workspace 的路径
revision: 1
last_synced_at: YYYY-MM-DDTHH:MM:SSZ
sources: []
---

## [以下正文逐字保留 raw_lark 原文，不得修改]

## 基本信息
- **项目名称**：[[垂类达人孵化]]
- **项目目标**：...
- **项目负责人**：[[李小明]]
- **项目核心成员**：[[张三]]（内容）、[[李四]]（运营）...
- **启动时间**：...
- **当前状态**：<🟢 / 🟡 / 🔴>

## 核心 KPI
| 指标 | 目标值 | 当前值 | 状态 |
|------|--------|--------|------|
| ... | ... | ... | ... |

## 风险阈值
| 指标 | 目标值 | 预警阈值 | 风险阈值 |
|------|--------|----------|----------|
| ... | ... | ... | ... |

## 本周进展
...

## 历史趋势
| 周次 | 指标1 | 指标2 | ... |
|------|-------|-------|-----|
| ... | ... | ... | ... |

## 资源需求
...

## 相关链接
- 周报归档
- 会议纪要
- ...

## [以上正文逐字保留 raw_lark 原文，不得修改]

## 实体引用
- [[实体名]] — 类型: project/brand/kol/person/platform/tool | 关系说明

## 概念引用
- [[概念名]] — 类型: SOP/strategy/metric/tool/workflow | 关系说明

## Contradictions
- 与 [[另一页面]] 的矛盾点：...
```

---

### 模板 5：部门周报 (dept-weekly)

适用于部门层级周报，如 `部门项目汇总/部门周报归档/` 下的文件。

```markdown
---
# 来源元数据（透传）
title: "<原文标题>"
doc_type: dept-weekly
scope: "public" | "dept" | "projects"
lark_url: "https://..."
lark_node_id: "..."
content_hash: "..."
status: active
# wiki 运行时（ingest 生成）
type: source
tags: [dept-weekly]
date: YYYY-MM-DD
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
source_file: "raw_lark/wiki/.../文件名.md"  # 相对 agent workspace 的路径
revision: 1
last_synced_at: YYYY-MM-DDTHH:MM:SSZ
sources: []
---

## [以下正文逐字保留 raw_lark 原文，不得修改]

## 一、部门总览
...

## 二、项目数据速览
| 项目 | PM | 状态 | 本周关键数据 | 本周人力投入 |
|------|----|------|-------------|-------------|
| [[垂类达人孵化]] | [[李小明]] | 🔴 | ... | ... |
| ... | ... | ... | ... | ... |

## 三、下周计划
| 项目 | 下周核心目标 | 关键事项 | 负责人 | 预期产出 |
|------|-------------|---------|--------|---------|
| ... | ... | ... | ... | ... |

## 四、部门精选知识
...

## [以上正文逐字保留 raw_lark 原文，不得修改]

## 实体引用
- [[实体名]] — 类型: project/brand/kol/person/platform/tool | 关系说明

## 概念引用
- [[概念名]] — 类型: SOP/strategy/metric/tool/workflow | 关系说明

## Contradictions
- 与 [[另一页面]] 的矛盾点：...
```

---

### 模板 6：部门 OnePage (dept-onepage)

适用于部门总览页，如 `部门项目汇总/部门 OnePage.md`。

```markdown
---
# 来源元数据（透传）
title: "<原文标题>"
doc_type: dept-onepage
scope: "public" | "dept" | "projects"
lark_url: "https://..."
lark_node_id: "..."
content_hash: "..."
status: active
# wiki 运行时（ingest 生成）
type: source
tags: [dept-onepage]
date: YYYY-MM-DD
source_file: "raw_lark/wiki/.../文件名.md"  # 相对 agent workspace 的路径
revision: 1
last_synced_at: YYYY-MM-DDTHH:MM:SSZ
sources: []
---

## [以下正文逐字保留 raw_lark 原文，不得修改]

## 基本信息
- **部门名称**：...
- **在跑项目数**：N 个

## 项目概况
| 项目 | PM | 启动时间 | 当前周期 | 状态 |
|------|----|----------|----------|------|
| [[垂类达人孵化]] | [[李小明]] | ... | ... | 🟡 |
| ... | ... | ... | ... | ... |

## 本周进展
...

## 资源需求
...

## 相关链接
- 部门周报归档
- ...

## [以上正文逐字保留 raw_lark 原文，不得修改]

## 实体引用
- [[实体名]] — 类型: project/brand/kol/person/platform/tool | 关系说明

## 概念引用
- [[概念名]] — 类型: SOP/strategy/metric/tool/workflow | 关系说明

## Contradictions
- 与 [[另一页面]] 的矛盾点：...
```

---

## 实体提取规则（精细化）

### 实体分类体系（MCN 领域）

| 类型 | 定义 | 示例 |
|------|------|------|
| `project` | 项目/业务线 | 垂类达人孵化、品牌代运营、直播电商、短视频内容矩阵、达人私域运营、虚拟IP孵化 |
| `brand` | 品牌/客户 | 雅诗兰黛、完美日记、花西子、欧莱雅、兰蔻、珀莱雅 |
| `kol` | 达人/KOL（含编号和昵称） | K001、K002、探店阿明、深夜食堂、一人食日记 |
| `person` | 内部人员（PM/负责人/执行人） | 张三、李四、王五、赵六 |
| `platform` | 内容/电商平台 | 抖音、小红书、B站、快手、淘宝直播、微信视频号 |
| `tool` | 工具/系统/软件 | Notion AI、剪映企业版、飞书多维表格、千川、DOU+ |

### 实体归一化标准（强制）

摄入时必须将以下漂移名称归一为标准简称：

| 标准简称 | 常见漂移名称（必须归一） |
|---------|------------------------|
| 垂类达人孵化 | 达人孵化、KOL孵化、达人孵化项目 |
| 品牌代运营 | 代运营、品牌运营 |
| 直播电商 | 直播带货、直播项目、直播电商项目 |
| 短视频内容矩阵 | 短视频矩阵、内容矩阵、短视频项目 |
| 达人私域运营 | 私域运营、私域项目 |
| 虚拟IP孵化 | 虚拟IP、虚拟人、虚拟IP项目 |
| 千川 | 巨量千川、千川投放 |
| 抖音 | 抖yin、DY |
| 小红书 | 红薯、XHS |

### 实体提取规则

1. **人员提取**：
   - 从「负责人：XXX」「PM：XXX」「核心成员：XXX」「执行人：XXX」等字段提取
   - 人名通常为 2-4 个中文汉字
   - **禁止提取**：职位称呼（如"负责人"、"PM"本身）、代词（"我"、"我们"）

2. **KOL/达人提取**：
   - 格式为 `K` + 3-4 位数字（如 K001、K002）
   - 达人人名（如"探店阿明"、"深夜食堂"）需结合上下文判断，有账号属性才提取
   - **禁止提取**：普通消费者名称、路人称呼

3. **品牌提取**：
   - 从「品牌：XXX」「客户：XXX」「合作方：XXX」字段提取
   - 知名美妆/消费品牌优先提取
   - **禁止提取**：泛化描述（"某品牌"、"头部品牌"）

4. **项目提取**：
   - 从「项目名称：XXX」字段提取
   - 或文档标题中明确的业务线名称
   - **禁止提取**：临时任务、子任务名称

5. **平台/工具提取**：
   - 明确提及的平台名（抖音、小红书、B站）
   - 明确提及的工具名（Notion AI、剪映、千川）
   - **禁止提取**：通用技术词（"AI"、"算法"、"系统"）单独作为工具

---

## 概念提取规则（精细化）

### 概念定义

概念是**可复用的方法论、流程、策略、指标或规范**，而非某次具体执行的结果或状态描述。

### 禁止提取的伪概念（过滤清单）

| 类型 | 示例 | 原因 |
|------|------|------|
| 纯数字 | `15万`、`132`、`4.5%` | 无语义，不可复用 |
| 数字+实体 | `2名达人`、`4名达人K001K004` | 具体数量描述 |
| 日期/时间 | `本周`、`下周`、`周一`、`4月`、`5月`、`Q2` | 时间标记，非概念 |
| 状态词 | `已完成`、`进行中`、`待启动`、`正常`、`风险`、`预警` | 状态描述，非概念 |
| 列表序号+内容 | `1目标回顾`、`3本周亮点`、`4项目管理` | 文档结构标记 |
| 具体事件/结果 | `B站粉丝突破5万纪念回`、`签约1家林十`、`ROI为132初步达标` | 一次性事件 |
| 过长描述 | 超过 20 个字的短语 | 不够精炼，不可复用 |
| 过短词 | 少于 3 个字 | 语义不足 |

### 允许提取的概念类型

| 类型 | 定义 | 示例 |
|------|------|------|
| `SOP` | 标准操作流程、规范、手册 | 达人筛选SOP、品牌合作流程、内容审核规范 |
| `strategy` | 策略、方案、打法 | 跨平台运营策略、内容差异化策略、流量投放策略 |
| `metric` | 关键指标、KPI、数据维度 | GMV、转化率、粉丝增长率、商单转化率、ROI |
| `tool` | 工具/技术方法（通用层） | AI脚本生成、智能剪辑、多平台分发 |
| `workflow` | 工作流程、协作机制 | 三级审核流程、周度复盘机制 |

### 概念归一化标准（强制）

| 标准名称 | 常见漂移名称 |
|---------|------------|
| 达人筛选SOP | 筛选标准、达人筛选标准、筛选流程 |
| 品牌合作SOP | 品牌合作流程、商务合作SOP |
| 内容策划SOP | 内容策划流程、选题策划规范 |
| 粉丝增长率 | 粉丝增长、涨粉率 |
| 商单转化率 | 变现转化率、接单转化率 |
| 内容差异化 | 差异化策略、内容差异化策略 |
| 跨平台运营 | 多平台运营、双平台分发 |

---

## 后处理规则（脚本侧强制执行）

### 实体类型纠正

生成实体页面后，应用以下规则纠正误分类：

1. **名称包含"项目"或匹配项目列表** → 强制归类为 `project`
2. **名称以 K 开头后跟数字** → 强制归类为 `kol`
3. **名称匹配已知品牌列表** → 强制归类为 `brand`
4. **名称匹配已知平台列表**（抖音/小红书/B站/快手/淘宝直播/微信视频号） → 强制归类为 `platform`
5. **名称匹配已知工具列表**（Notion/剪映/千川/DOU+/飞书） → 强制归类为 `tool`
6. **2-4 字中文人名，且不在上述类别中** → 归类为 `person`

### 概念去重与清理

1. **移除纯数字、数字开头、日期词、状态词**（参见上方过滤清单）
2. **合并同一概念的不同变体**：
   - 去除前后缀（"SOP"、"流程"、"规范"、"策略"）后比较核心词
   - 若核心词相同，合并为归一化后的标准名称
3. **长度过滤**：概念名必须在 3-20 字之间
4. **禁止将实体名放入概念**：若概念名与已提取实体名相同，丢弃该概念

---

### Step 4 — 更新 workspace/knowledge/wiki/index.md

在对应 scope 分区下添加/更新条目：

```markdown
- [标题]({scope}/sources/{slug}.md) — 一句话摘要
```

如果条目已存在（同一 slug）→ 替换为新的摘要。

---

### Step 5 — 更新 workspace/knowledge/wiki/overview.md

如果该文档引入了新的项目、重要的方法论或改变了整体认知：
- 在 overview 中追加或修订相关段落
- 保持 overview 是"活着的综合"，不是简单罗列

---

### Step 6 — 创建/更新 Entity Pages

如果文档中提到了**关键人物、公司、项目、产品、品牌**，且该实体尚未有独立页面或已有页面需要更新：

写入 `workspace/knowledge/wiki/entities/{Name}.md`（TitleCase 或原始中文名）：

```markdown
---
title: "实体名称"
type: entity
tags: [project | brand | kol | person | platform | tool]
sources: [{slug}]
last_updated: YYYY-MM-DD
---

## 简介
一句话定义。

## 关键信息
- 类型: project/brand/kol/person/platform/tool
- 标准名称: （如有漂移名称，注明标准简称）

## 关联来源
- [[SourcePage]] — 关系说明
```

**注意**：实体页面必须应用「实体归一化标准」，禁止因名称漂移创建重复页面。

---

### Step 7 — 创建/更新 Concept Pages

如果文档中提到了**方法论、框架、SOP、理论**，且该概念尚未有独立页面：

写入 `workspace/knowledge/wiki/concepts/{Name}.md`（TitleCase 或原始中文名）：

```markdown
---
title: "概念名称"
type: concept
tags: [SOP | strategy | metric | tool | workflow]
sources: [{slug}]
last_updated: YYYY-MM-DD
---

## 定义
一句话定义。

## 核心要点
- （关键要素）

## 应用场景
- （适用场景）

## 关联来源
- [[SourcePage]] — 关系说明
```

**注意**：概念必须经过「概念过滤清单」检查，禁止将伪概念写入概念页面。

---

### Step 8 — 检测矛盾

对比源文档的关键论断与 `workspace/knowledge/wiki/sources/` 中近期 5 个页面的内容。如发现矛盾：
- 在 Source Page 的 `## Contradictions` 中记录
- 如矛盾涉及已有 Entity/Concept 页面，也在对应页面中标注

---

### Step 9 — 追加日志

追加到 `workspace/knowledge/wiki/log.md`（prepend，最新在最前）：

```markdown
## [YYYY-MM-DD] ingest | 文档标题
- Scope: {scope}
- Slug: {slug}
- Revision: {revision}
- 文档类型: {doc_type}
- 新增实体: [[Name1]], [[Name2]]
- 新增概念: [[Concept1]]
```

---

### Step 10 — Post-ingest 验证

1. **Broken links**：检查本次创建/修改的所有页面中 `[[WikiLink]]` 是否指向了不存在的页面。
2. **Index sync**：确认新 source page 的 slug 出现在 `workspace/knowledge/wiki/index.md` 中。
3. **伪概念检查**：抽查概念页面，确认无过滤清单中的垃圾概念。
4. **内容完整性检查**：确认 Source Page 中保留了原文所有表格行、Q&A 对、列表项。
5. 打印变更摘要：
   ```
   Ingested: 标题
   Scope: {scope}
   文档类型: {doc_type}
   Created: X pages (list)
   Updated: index.md, overview.md, log.md
   Validation: passed / N broken links / M pseudo-concepts
   ```

---

## 命名与路径规范

| 类型 | 路径 | 文件名规范 |
|------|------|-----------|
| Source (public/dept) | `workspace/knowledge/wiki/{scope}/sources/` | `kebab-case.md` |
| Source (projects) | `workspace/knowledge/wiki/projects/{project_id}/sources/` | `kebab-case.md` |
| Entity | `workspace/knowledge/wiki/entities/` | `TitleCase.md` 或原始中文名（保留语义） |
| Concept | `workspace/knowledge/wiki/concepts/` | `TitleCase.md` 或原始中文名（保留语义） |
| Index | `workspace/knowledge/wiki/index.md` | — |
| Overview | `workspace/knowledge/wiki/overview.md` | — |
| Log | `workspace/knowledge/wiki/log.md` | — |

---

## 红线

- **不修改 raw_lark/ 下的原始文件**（只读）
- **不编造原文没有的信息**
- **不遗漏 frontmatter**（lark_url、content_hash 必须保留）
- **必须生成 [[Wikilink]]**（这是图谱的边）
- **跨 scope 引用用相对路径**：`[[../entities/Name]]` 或直接用 `[[Name]]`（同目录解析）
- **禁止创建重复实体/概念页面**：同一实体/概念的不同称呼必须先归一化再写入
- **禁止提取伪概念**：必须经过过滤清单检查
- **禁止丢失原文表格/列表/Q&A**：结构化数据必须完整保留，不得因"简化"而省略行或条目
