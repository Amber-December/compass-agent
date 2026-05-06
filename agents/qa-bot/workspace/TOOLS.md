# TOOLS.md — qa-bot 工具速查

> Skills 定义工具的用法，这个文件记录 qa-bot 专属的配置和速查。

---

## 本地工具脚本

工具位于 `tools/` 目录（通过 workspace 软链接访问）：

| 工具 | 用途 | 典型调用 |
|------|------|---------|
| `wiki_query.py` | 知识库查询 | `python tools/wiki_query.py "问题" --scope kol-incubation --json` |
| `data_query.py` | 数据查询 | `python tools/data_query.py --project kol-incubation --week latest` |
| `graph_query.py` | 图谱查询 | `python tools/graph_query.py "关键词" --serve` |

### wiki_query.py 速查

```python
from tools.wiki_query import query_wiki

# 知识查询（带权限隔离）
result = query_wiki("达人筛选标准", scope="kol-incubation")
# result = {"context": "...", "sources": [...], "scope": "kol-incubation"}
```

### data_query.py 速查

```python
from tools.data_query import query_data

# 数据查询
result = query_data(project="kol-incubation", week="latest")
# result = {"kpi": {...}, "tasks": [...], "risks": [...]}
```

### graph_query.py 速查

```python
from tools.graph_query import query_graph, search_subgraph, generate_subgraph_html

# 完整图谱
result = query_graph(open_browser=False)

# 关键词子图
subgraph = search_subgraph("垂类达人孵化", hops=1)
html_path = generate_subgraph_html(subgraph)
```

---

## 飞书相关配置

### 群聊绑定（chatBindings）

| chat_id | 群名称 | scope |
|---------|--------|-------|
| `oc_d2f8a9f659fce3626572c2bd80083d23` | 垂类达人孵化项目群 | `kol-incubation` |
| `oc_b4225b78e62121080ceafc9c8c96461a` | 品牌代运营项目群 | `brand-ops` |

### Scope 可访问范围

| scope | 可读取路径 |
|-------|-----------|
| `None` | public/ + dept/ + entities/ + concepts/ + projects/* |
| `dept` | public/ + dept/ + entities/ + concepts/ |
| `kol-incubation` | public/ + dept/ + projects/kol-incubation/ + entities/ + concepts/ |
| `brand-ops` | public/ + dept/ + projects/brand-ops/ + entities/ + concepts/ |
| `live-commerce` | public/ + dept/ + projects/live-commerce/ + entities/ + concepts/ |
| `short-video` | public/ + dept/ + projects/short-video/ + entities/ + concepts/ |
| `private-domain` | public/ + dept/ + projects/private-domain/ + entities/ + concepts/ |
| `virtual-ip` | public/ + dept/ + projects/virtual-ip/ + entities/ + concepts/ |

---

## Agent 调度速查

| 意图 | 触发词 | 目标 Agent | 调用方式 |
|------|--------|-----------|---------|
| 刷新知识库 | "刷新知识库" "/wiki-sync" | wiki-manager | 内部调度 |
| 生成周报 | "生成周报" "部门看板" | weekly-reporter | 内部调度 |
| 推送卡片 | "发通知" "推送卡片" | card-builder | 内部调度 |

---

## 环境路径

```
workspace/
├── workspace/knowledge/wiki/      → 知识库（全局共享，只读）
├── workspace/knowledge/data/      → 数据缓存（全局共享，只读）
├── workspace/knowledge/graph/     → 图谱数据（全局共享，只读）
├── tools/     → 工具脚本（软链接）
└── skills/    → OpenClaw Skills（软链接）
```