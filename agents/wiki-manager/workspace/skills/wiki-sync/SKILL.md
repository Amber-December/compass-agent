---
name: wiki-sync
description: "wiki-sync"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 飞书 Wiki 增量同步 Skill — 检测变更、拉取文档、预处理清洗，为 ingest 提供干净的 raw 源

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/wiki-sync/`

## 触发条件

- 定时：每周一 8:30 全量同步，每 6 小时增量检查
- 手动：用户说 "同步 Wiki" / "刷新知识库" 时触发

## 核心能力

### 1. 读取配置

从 `config/sources.yaml` 获取：
- space_id: 飞书 Wiki 空间 ID
- scope_rules: 文档 scope 映射规则
- nodes: 需要同步的 Wiki 节点列表

### 2. 检测变更

对比 sync_state.json 中的 content_hash：
- hash 相同 → 跳过
- hash 不同 / 新文档 → 拉取

### 3. 拉取文档

通过 lark-cli 调用飞书 API：
```bash
lark-cli docs +fetch --doc <obj_token> --format=json
```

### 4. 预处理清洗（Sync 阶段完成，减轻 Ingest 负担）

拉取后、写入 `raw_lark/wiki/` **之前**，执行三项清洗：

#### 4.1 `lark-table` XML → Markdown Pipe Table

飞书导出的表格使用 `<lark-table><lark-tr><lark-td>` XML 格式，token 开销是标准 markdown pipe table 的 5-10 倍。sync 阶段用正则提取转换为 pipe table，显著降低后续 ingest 的 LLM token 消耗。

#### 4.2 移除冗余脚注

删除文末的 `**飞书 Wiki 在线地址**：...` 脚注（该信息已包含在 frontmatter 的 `lark_url` 中）。

#### 4.3 自动判定 `doc_type`

根据路径、标题、正文结构自动判定文档类型并写入 frontmatter：

| doc_type | 判定依据 |
|---------|---------|
| `project-weekly` | `/周报归档/` 路径，或标题含 Week + 周报 + 数据看板 |
| `dept-weekly` | `/部门周报归档/` 路径，或标题含部门周报 |
| `meeting` | `/会议纪要/` 路径，或含基本信息+讨论要点+行动项 |
| `project-doc` | `/项目文档/` 路径，或含手册/SOP/规范/方案 + 结构化流程 |
| `project-onepage` | 标题含 OnePage + 核心KPI/风险阈值 |
| `dept-onepage` | 标题含部门 OnePage + 项目概况 |
| `default` | 以上均不匹配 |

### 5. 保存原始镜像

写入 `raw_lark/wiki/`（agent workspace 下的相对路径），frontmatter **仅保留来源元数据**（不含 wiki 运行时状态）：

```yaml
---
title: "..."
doc_type: "..."          # 自动判定
scope: public | dept | projects
project_id: "..."        # 仅 projects scope
lark_url: "https://..."
lark_node_id: "..."
content_hash: "sha256..." # body 的 hash，用于 ingest 增量判断
fetched_at: "..."
status: active | archived
---
```

**注意**：frontmatter 中**不出现**以下 wiki 运行时字段（由 ingest 阶段生成）：
- `type: source`
- `source_file`
- `revision`
- `last_synced_at`

## 输出目录结构

```
raw_lark/wiki/
├── public/          # 公共文档（SOP、培训、指南）
├── dept/            # 部门级文档（周报、OnePage）
└── projects/        # 项目级文档
    ├── kol-incubation/
    ├── brand-ops/
    ├── live-commerce/
    ├── short-video/
    ├── private-domain/
    └── virtual-ip/
```

## 与 wiki-ingest 的关系

```
wiki-sync（拉取 + 预处理清洗）
    └── 完成后触发
        └── wiki-ingest（LLM 语义提取：实体/概念/矛盾）
```

设计原则：**格式清洗在 sync 的脚本层完成，语义提取在 ingest 的 LLM 层完成**。这样 ingest 阶段拿到的是干净 markdown，只需做它擅长的事（理解、提取、关联），而不需要消耗 token 在 XML 解析和格式转换上。

## 存量清洗

对于已存在的 raw_lark 文件，在 workspace 目录下运行：
```bash
python tools/clean_raw_lark.py
```
该脚本会批量执行表格转换、脚注移除、frontmatter 重建。

## 输出格式（强制）

同步完成后，**只输出一条统计消息**：

```markdown
📄 Wiki 文档同步完成
- 新增：{N} 篇
- 变更：{N} 篇
- 未变更：{N} 篇
```

**绝对禁止**：
- 输出思考过程、分析步骤、中间状态
- 暴露本地文件路径或内部操作细节
- 分多条消息输出

## 红线

- 不修改已存在的本地文档（除非检测到变更）
- 飞书侧删除的文档改为 status: archived，不物理删除
- 权限不足时明确告知缺失的 scope
- **sync 阶段不引入 LLM 调用**（所有清洗都是确定性脚本）
- **严禁输出思考过程**，只输出统计结果
