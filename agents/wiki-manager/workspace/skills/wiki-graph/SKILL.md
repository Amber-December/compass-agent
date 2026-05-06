---
name: wiki-graph
description: "wiki-graph"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 知识图谱构建与可视化 — 从 workspace/knowledge/wiki/ 目录生成可交互的知识图谱，支持显式链接提取 + LLM 语义推断

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/wiki-workspace/knowledge/graph/`

## 触发条件

- **自动**：`wiki-ingest` 完成后，如条件满足（`step-3.ingested_pages > 0`），由 workflow 自动触发
- **手动**：用户说 "构建知识图谱" / "更新图谱" / "/wiki-graph" / "build graph" 时触发
- **定时**：每周一 8:35（紧随全量同步与 ingest 之后）

## 核心能力

### 1. 两-pass 建图

基于 `tools/build_graph.py` 执行：

**Pass 1 — 显式链接提取（EXTRACTED）**
- 扫描 `workspace/knowledge/wiki/` 下所有 `.md` 文件（排除 `index.md`、`log.md`、`lint-report.md`）
- 正则提取 `[[PageName]]` 格式的 wikilink
- 生成确定性边，confidence = 1.0

**Pass 2 — 语义推断（INFERRED / AMBIGUOUS）**
- 对变更过的页面，调用 LLM 推断与其他页面的隐式语义关系
- 缓存机制：基于 SHA256 内容哈希，未变更页面直接复用历史推断结果
- 断点续传：支持 `.inferred_edges.jsonl` checkpoint，中断后可恢复
- confidence >= 0.7 → `INFERRED`，< 0.7 → `AMBIGUOUS`

### 2. 社区检测

- 使用 Louvain 算法（networkx）检测知识社区
- 为同一社区的节点分配相同颜色，便于视觉识别知识聚类
- 节点大小基于 degree（连接数）

### 3. 健康报告（可选）

当用户要求报告或 `--report` 时，生成结构化的图谱健康分析：

| 指标 | 说明 | 阈值 |
|------|------|------|
| Orphan Nodes | 零连接的孤立页面 | 目标 < 10% |
| God Nodes | 连接度远超平均的枢纽页 | degree > μ+2σ |
| Fragile Bridges | 仅由 1 条边连接的社区对 | 需加固 |
| Phantom Hubs | 被 2+ 页面引用但尚未创建的页面 | 优先创建 |
| Link Density | 图谱密度 | — |

### 4. 可视化输出

生成两个文件：

- **`workspace/knowledge/graph/graph.json`** — 机器可读（nodes + edges + built 时间戳）
- **`workspace/knowledge/graph/graph.html`** — 可交互可视化（vis.js），支持：
  - 节点搜索与聚焦
  - 点击节点查看完整 markdown 内容
  - Edge 类型过滤（EXTRACTED / INFERRED / AMBIGUOUS）
  - Confidence 阈值滑动条
  - 邻居高亮

## 执行步骤

1. **读取 wiki 目录** — 收集所有 `.md` 页面
2. **Pass 1: 提取节点与显式边**
   - 解析 frontmatter 获取 title、type
   - 提取 wikilink 生成 EXTRACTED 边
3. **Pass 2: 语义推断**（除非 `--no-infer`）
   - 检查 SHA256 缓存，跳过未变更页面
   - 对新增/修改页面调用 LLM 推断关系
   - 更新 checkpoint 与缓存
4. **边去重** — 同一对节点间保留 confidence 最高的边
5. **社区检测** — Louvain 算法分配 community id 与颜色
6. **Degree 计算** — 用于节点大小映射
7. **写入输出** — `workspace/knowledge/graph/graph.json` + `workspace/knowledge/graph/graph.html`
8. **追加日志** — `workspace/knowledge/wiki/log.md` 记录 graph 重建事件
9. **生成报告**（如 `--report`）— 输出健康分析，可选保存到 `workspace/knowledge/graph/graph-report.md`
10. **打开浏览器**（如 `--open`）

## 与 wiki-ingest 的关系

```
wiki-ingest（生成/更新 workspace/knowledge/wiki/ 页面）
    └── 触发
        └── wiki-graph（基于最新 wiki 重建图谱）
```

- wiki-graph **只读** `workspace/knowledge/wiki/` 目录，不修改任何 wiki 页面
- 依赖 wiki-ingest 生成的 `[[wikilinks]]` 作为 Pass 1 的边来源
- ingest 新增的页面会自动被图谱收录

## 参数说明

| 参数 | 说明 | 默认 |
|------|------|------|
| `--no-infer` | 跳过 Pass 2 语义推断，仅使用显式 wikilink | false |
| `--clean` | 删除 inference checkpoint，强制全量重新推断 | false |
| `--report` | 生成并打印图谱健康报告 | false |
| `--save` | 将报告保存到 `workspace/knowledge/graph/graph-report.md` | false |
| `--open` | 构建后在浏览器打开 `workspace/knowledge/graph/graph.html` | false |

## 依赖

- **networkx** — Louvain 社区检测（可选，缺失时社区检测跳过）
- **openai** — LLM 语义推断（使用环境变量 `MOONSHOT_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`，或 `openclaw.json` 配置）

## 红线

- **只读 workspace/knowledge/wiki/** — 绝不修改、删除 wiki 页面
- **不编造链接** — INFERRED 边必须有 LLM 返回的语义依据
- **缓存必须命中** — 未变更页面不得重复调用 LLM 推断
- **断点可恢复** — 中断后重新运行应从中断处继续，而非从头开始
