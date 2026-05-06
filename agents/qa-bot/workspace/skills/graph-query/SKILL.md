---
name: graph-query
description: "知识图谱查询与展示 — scope 感知子图搜索 + Markdown 链接跳转交互式 vis.js 页面"
metadata:
  {
    "openclaw":
      {
        "emoji": "🕸️",
      },
  }
---

# graph-query Skill

> 知识图谱查询与展示 — scope 感知子图搜索 + Markdown 链接跳转交互式 vis.js 页面

## 归属

- **Agent**: qa-bot
- **路径**: `agents/qa-bot/workspace/skills/graph-query/`
- **工具**: `agents/qa-bot/workspace/tools/graph_query.py`

## 触发条件

- 用户意图被识别为 **图谱查询**
- 典型问法：
  - 完整图谱："知识图谱"、"关系图"、"看看图谱"、"知识网络"
  - 子图查询："垂类达人孵化的图谱"、"看看李小明的关系图"
  - 模糊查询："看看咱们项目的图谱"（scope 感知）

## 核心能力

### 1. scope 感知 — 默认展示本项目子图

当用户在项目群中查询图谱时，**默认只展示当前 scope 对应的项目子图**，而非完整图谱。

**规则**：

| scope | 用户提问 | 默认搜索关键词 | 展示范围 |
|-------|----------|---------------|----------|
| `kol-incubation` | "看看图谱" | "垂类达人孵化" | 垂类达人孵化子图 |
| `brand-ops` | "看看图谱" | "品牌代运营" | 品牌代运营子图 |
| `live-commerce` | "图谱" | "直播电商" | 直播电商子图 |
| `short-video` | "关系图" | "短视频内容矩阵" | 短视频内容矩阵子图 |
| `private-domain` | "知识图谱" | "达人私域运营" | 达人私域运营子图 |
| `virtual-ip` | "看看图谱" | "虚拟IP孵化" | 虚拟IP孵化子图 |
| `dept` / `None` | "看看图谱" | — | 完整部门级图谱（所有项目聚合） |

**跨项目子图查询**：
- 用户明确指定其他项目："看看直播电商的图谱"
- 按指定关键词搜索子图，不受 scope 默认规则限制
- 子图内容本身不涉及敏感数值，属于知识关联可视化，**可以跨 scope 展示**

---

### 2. 子图搜索与交互式页面生成

支持按关键词搜索子图，生成自包含的交互式 vis.js HTML：

1. 在节点 `label` 和 `id` 中模糊匹配关键词
2. 提取匹配节点及其 N 跳邻居（默认 1 跳）
3. 生成高亮匹配节点的交互式子图 HTML
4. 将 HTML 保存到 `workspace/knowledge/graph/subgraph_<keyword>.html`


**工具调用**：
```bash
python tools/graph_query.py "垂类达人孵化" --hops 1
```

---

### 3. Markdown 链接 — 可点击的图谱回复

qa-bot 返回的图谱查询回复为 **Markdown 格式**，包含子图概况 + 可点击的链接：

1. **子图概况**：节点数、边数、核心节点列表
2. **交互式链接**：点击后跳转交互式图谱页面

**回复格式**：
```markdown
🕸️ **垂类达人孵化 — 知识子图**

节点数：53 ｜ 边数：194 ｜ 核心节点：李小明、张三、达人筛选SOP

🔗 [点击打开交互式图谱](http://localhost:8766.html)
```

---

## 查询链路

### 项目群子图查询（默认）
```
用户提问（scope = kol-incubation）: "看看图谱"
    └── 意图识别（intent skill）
        └── 图谱查询 → graph-query skill
            ├── 识别 scope = kol-incubation
            ├── 默认关键词 = "垂类达人孵化"
            ├── 调用 graph_query.search_subgraph("垂类达人孵化", hops=1)
            │   ├── 在节点 label/id 中匹配关键词
            │   ├── 提取匹配节点 + 1 跳邻居
            │   └── 返回子图数据
            ├── 生成子图 HTML
            │   └── 保存到 workspace/knowledge/graph/subgraph_垂类达人孵化.html
            ├── 构建 Markdown 回复
            │   ├── 子图概况（节点数/边数/核心节点）
            │   └── 可点击链接（跳转 http://localhost:8766.html）
            └── 返回 Markdown → 飞书群聊展示
```

### 指定子图查询
```
用户提问："看看直播电商的图谱"
    └── 意图识别
        └── 图谱查询 → graph-query skill
            ├── 提取关键词 = "直播电商"
            ├── 调用 search_subgraph("直播电商", hops=1)
            ├── 生成子图 HTML（subgraph_直播电商.html）
            └── 构建 Markdown 链接回复
```

## 工具使用

### 调用 graph_query.py

```python
from tools.graph_query import search_subgraph, generate_subgraph_html

# scope 感知的默认子图搜索
scope = "kol-incubation"
keyword = scope_to_keyword(scope)  # kol-incubation → "垂类达人孵化"

subgraph = search_subgraph(keyword, hops=1)
# subgraph = {
#     "keyword": "垂类达人孵化",
#     "matched_nodes": [...],
#     "nodes": [...],
#     "edges": [...],
#     "context": "子图描述文本",
#     "node_count": 53,
#     "edge_count": 194
# }

# 生成子图 HTML（文件名基于 keyword，如 subgraph_垂类达人孵化.html）
html_path = generate_subgraph_html(subgraph)
# 保存到: workspace/knowledge/graph/subgraph_垂类达人孵化.html
```

### scope → 关键词映射

```python
SCOPE_KEYWORD_MAP = {
    "kol-incubation": "垂类达人孵化",
    "brand-ops": "品牌代运营",
    "live-commerce": "直播电商",
    "short-video": "短视频内容矩阵",
    "private-domain": "达人私域运营",
    "virtual-ip": "虚拟IP孵化",
}
```

### 构建 Markdown 回复

```python
def build_graph_reply(subgraph, scope):
    """构建图谱查询 Markdown 回复"""
    keyword = SCOPE_KEYWORD_MAP.get(scope, "部门")
    # 链接中的文件名必须与 generate_subgraph_html 生成的文件名一致（基于 keyword）
    graph_url = f"http://localhost:8766/subgraph_{keyword}.html"
    core_nodes = ", ".join(subgraph["matched_nodes"][:3])

    return (
        f"🕸️ **{keyword} — 知识子图**\n\n"
        f"节点数：{subgraph['node_count']} ｜ 边数：{subgraph['edge_count']} ｜ 邻居深度：1 跳\n\n"
        f"**核心节点**：{core_nodes}\n\n"
        f"🔗 [点击打开交互式图谱]({graph_url})"
    )
```

## 回答生成规范（强制）

**绝对禁止**：
- 输出思考过程、推理步骤、分析过程
- 说"让我看看"、"根据图谱分析"等中间状态
- 分多条消息输出，只输出一条最终消息
- **严禁返回 JSON 或飞书消息卡片** — 必须返回 Markdown 文本
- 暴露本地文件路径（如 `workspace/`、`file://`，服务未部署时除外）

**必须包含**：
- 子图概况（节点数、边数、核心节点）
- **可点击的链接**（Markdown `[描述](URL)` 格式）
- 只输出一条消息（Markdown 文本）

**输出示例**（Markdown）：
```markdown
🕸️ **垂类达人孵化 — 知识子图**

节点数：53 ｜ 边数：194 ｜ 邻居深度：1 跳

**核心节点**：垂类达人孵化、李小明、达人筛选SOP

🔗 [点击打开交互式图谱](http://localhost:8766/subgraph_垂类达人孵化.html)
```

**服务未部署时的降级方案**：
```markdown
🕸️ **垂类达人孵化 — 知识子图**

节点数：53 ｜ 边数：194 ｜ 核心节点：李小明、张三、达人筛选SOP

📎 [下载图谱 HTML 文件](file:///Users/amber/compass-agent/workspace/knowledge/graph/subgraph_垂类达人孵化.html)
```

## 缺失处理

如果图谱尚未生成：
- 返回 Markdown："知识图谱尚未生成，请联系 wiki-manager 执行构建"
- 提供构建命令提示：`python agents/wiki-manager/tools/build_graph.py`

## 红线

- **严禁输出思考过程** — 只输出一条消息（Markdown），禁止展示推理步骤
- **严禁返回 JSON 或飞书卡片** — 图谱查询回复必须是 Markdown 文本 + 可点击链接
- **graph.json 只读**，不修改原始图谱数据
- **子图 HTML 允许写入** `workspace/knowledge/graph/` 目录
- **不暴露本地文件路径** — 链接 URL 必须是可公开访问的地址（服务未部署时除外）
- **不编造节点关系**，基于实际 graph.json 数据
- **文件名必须一致** — `generate_subgraph_html` 生成的文件名（基于 keyword）与 `build_graph_reply` 构造的 URL 必须对应
