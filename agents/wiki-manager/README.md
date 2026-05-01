# Wiki 管理助手 (wiki-manager)

负责飞书 Wiki 知识库的文档推送、读取、结构管理和本地 LLM-Wiki 知识底座构建。

## 职责

- 📤 推送本地 Markdown 文档到飞书 Wiki
- 📥 读取飞书 Wiki 文档到本地
- 🏗️ 管理 Wiki 目录结构（创建/移动/删除节点）
- 📚 **构建本地 LLM-Wiki 符号化知识底座**（核心能力）
  - 知识编译：将飞书文档编译为结构化 Markdown
  - 实体/概念提取：自动创建实体页和概念页
  - 知识图谱：两-pass 建图（显式 wikilink + LLM 语义推断）
  - 问答检索：关键词匹配 + 图邻居扩展，带飞书链接引用

## 触发方式

- 人工指令："把 docs/MCN lark/ 下的文档推到 Wiki"
- 定时任务：每周同步 Wiki 更新到本地
- 被动触发：qa-bot 检索知识底座时自动使用

## 输入输出

| 输入 | 输出 |
|------|------|
| 本地 Markdown 文件 | 飞书 Wiki 文档 |
| Wiki 节点 token | 本地 Markdown 文件 |
| 目录结构调整指令 | 更新后的 Wiki 结构 |
| 飞书原始文档 | 结构化 wiki/sources/ + entities/ + concepts/ |

## 配置

### 环境变量

在 `.env` 中配置：

```bash
# Wiki 空间配置
WIKI_SPACE_ID=                # MCN 知识库空间 ID
WIKI_MCN_NODE_TOKEN=          # MCN 根节点 token

# LLM 配置（用于知识编译和图谱构建）
MOONSHOT_API_KEY=             # Moonshot API Key
LLM_BASE_URL=https://api.kimi.com/coding/
LLM_MODEL=kimi-k2-6
```

### 本地知识库结构（wiki/）

```
wiki/
├── index.md              # 知识库索引（自动维护）
├── overview.md           # 全局综合页（自动维护）
├── log.md                # 操作日志（追加模式）
├── sources/              # 来源页（每份飞书文档对应一页）
│   └── <slug>.md         # 结构化摘要，含 frontmatter（lark_url 等）
├── entities/             # 实体页（人、项目、品牌）
│   └── <EntityName>.md   # 实体定义和关系
├── concepts/             # 概念页（SOP、方法论、规范）
│   └── <ConceptName>.md  # 概念定义和引用
└── syntheses/            # 综合页（qa-bot 问答沉淀）
    └── <slug>.md         # 问答综合结果
```

### 图谱输出（graph/）

```
graph/
├── graph.json            # 节点和边数据（供 wiki_query.py 检索）
├── graph.html            # 交互式可视化（vis.js）
├── graph-report.md       # 图谱健康报告（可选）
├── .cache.json           # SHA256 增量缓存
└── .inferred_edges.jsonl # 语义推断检查点（断点续传）
```

## 核心工具

### 1. 知识编译：wiki_ingest.py

将飞书文档（Markdown 格式）编译为结构化知识底座。

```bash
# 单文件 ingest
python tools/wiki_ingest.py workspace/raw_lark/wiki/垂类达人孵化/项目\ OnePage.md

# 批量 ingest 目录
python tools/wiki_ingest.py --batch workspace/raw_lark/wiki/

# 仅验证（检查断链和未索引页面）
python tools/wiki_ingest.py --validate-only
```

**输出**：
- `wiki/sources/<slug>.md` — 结构化来源页（含 lark_url frontmatter）
- `wiki/entities/<Name>.md` — 实体页（自动提取）
- `wiki/concepts/<Name>.md` — 概念页（自动提取）
- 自动更新 `wiki/index.md` 和 `wiki/overview.md`

### 2. 知识检索：wiki_query.py

基于符号化知识底座回答用户问题，支持图邻居扩展。

```bash
# 命令行查询
python tools/wiki_query.py "垂类达人孵化的粉丝增长率为什么下滑？"
python tools/wiki_query.py "达人筛选标准有哪些硬性指标？" --save

# API 调用
python -c "from tools.wiki_query import query_wiki; print(query_wiki('问题', project_scope='垂类达人孵化'))"
```

**检索策略**：
1. 关键词匹配 `wiki/index.md`（CJK 双字滑动窗口）
2. 图邻居扩展 `graph/graph.json`（置信度 ≥ 0.7 的 INFERRED 边）
3. 总是包含 `wiki/overview.md`
4. LLM 综合答案，要求标注 `[[PageName]]` 来源引用

### 3. 图谱构建：build_graph.py

两-pass 构建知识图谱，支持增量更新和交互式可视化。

```bash
# 完整重建（含语义推断）
python tools/build_graph.py

# 跳过语义推断（更快，仅提取显式 wikilink）
python tools/build_graph.py --no-infer

# 构建后打开浏览器查看
python tools/build_graph.py --open

# 生成健康报告
python tools/build_graph.py --report --save

# 强制全量重新推断（清除缓存）
python tools/build_graph.py --clean
```

**图谱特性**：
- **Pass 1**：提取 `[[Wikilink]]` 作为 EXTRACTED 边（置信度 1.0）
- **Pass 2**：LLM 推断隐式语义关系作为 INFERRED（≥ 0.7）/ AMBIGUOUS（< 0.7）边
- **Louvain 社区检测**：自动聚类相关主题，用不同颜色标识
- **增量更新**：SHA256 缓存，仅处理变更页面
- **断点续传**：`.inferred_edges.jsonl` 检查点，避免重复调用 LLM

## 使用方法

### 推送本地文档到飞书 Wiki

```bash
cd /Users/amber/lark-knowledge-agent
python scripts/wiki_push.py \
  --space <space_id> \
  --parent <parent_node_token> \
  --dir "docs/MCN lark"
```

### 读取飞书 Wiki 到本地

```bash
# 获取节点信息
lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}'

# 读取文档内容
lark-cli docs +fetch --doc <obj_token> > workspace/raw_lark/<filename>.md
```

### 管理 Wiki 结构

```bash
# 创建节点
lark-cli wiki +node-create --space <space_id> --parent <parent> --type docx --title "节点标题"

# 移动节点
lark-cli wiki +move --node <node_token> --to_space <space_id> --to_parent <parent>

# 列出子节点
lark-cli wiki nodes list --params '{"space_id":"<space_id>"}'
```

## 当前状态

- [x] 本地 MCN 文档已准备（5 份）
- [x] 推送脚本已创建
- [x] 操作指南已创建
- [x] 知识库结构已定义
- [x] **符号化知识编译工具（wiki_ingest.py）已就绪**
- [x] **图增强检索工具（wiki_query.py）已就绪**
- [x] **知识图谱构建工具（build_graph.py）已就绪**
- [x] **wiki/ 目录结构已初始化（index.md / overview.md / log.md）**
- [ ] 待获取目标 Wiki 空间权限
- [ ] 待执行首次推送

## 依赖

- `shared/skills/lark-api`
- `shared/skills/prompt-template`
- `shared/skills/wiki-push`
- `shared/skills/wiki-read`
- `shared/skills/wiki-structure`
- Python 依赖：`openai`, `pyyaml`, `networkx`（可选，用于社区检测）
