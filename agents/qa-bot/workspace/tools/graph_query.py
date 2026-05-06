#!/usr/bin/env python3
"""
Compass QA-Bot Graph Query — 知识图谱检索工具（配合 OpenClaw LLM Skill 使用）

功能：
- 返回知识图谱信息，供 OpenClaw LLM 综合生成回答
- 支持关键词子图搜索与交互式 HTML 生成
- 支持本地 HTTP 服务一键启动

Usage:
    python tools/graph_query.py
    python tools/graph_query.py "垂类达人孵化" --serve
    python tools/graph_query.py --open

API:
    from tools.graph_query import query_graph, describe_graph, search_subgraph
    result = query_graph(open_browser=False)
    subgraph = search_subgraph("垂类达人孵化", hops=1)
"""

import os
import sys
import json
import argparse
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path
from typing import Optional, Union

def _find_repo_root() -> Path:
    """向上查找包含 openclaw.json 的项目根目录"""
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "openclaw.json").exists():
            return parent
    return p.parent.parent.parent.parent

# 路径常量
REPO_ROOT = _find_repo_root()
GRAPH_JSON = REPO_ROOT / "workspace" / "knowledge" / "graph" / "graph.json"
GRAPH_HTML = REPO_ROOT / "workspace" / "knowledge" / "graph" / "graph.html"


def read_graph_data() -> dict:
    """读取图谱数据"""
    if not GRAPH_JSON.exists():
        return {}

    try:
        with open(GRAPH_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def build_graph_context(graph_data: dict) -> str:
    """构建图谱上下文，供 LLM 使用"""
    if not graph_data:
        return "知识图谱尚未生成。"

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    context_parts = []
    context_parts.append(f"知识图谱概况：")
    context_parts.append(f"- 节点数：{len(nodes)}")
    context_parts.append(f"- 边数：{len(edges)}")
    context_parts.append("")

    # 统计节点类型
    node_types = {}
    for node in nodes:
        node_type = node.get("type", "unknown")
        node_types[node_type] = node_types.get(node_type, 0) + 1

    context_parts.append("节点类型分布：")
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        context_parts.append(f"  - {node_type}: {count}")

    context_parts.append("")

    # 核心节点（度最高的）
    node_degrees = {}
    for edge in edges:
        if "from" in edge:
            node_degrees[edge["from"]] = node_degrees.get(edge["from"], 0) + 1
        if "to" in edge:
            node_degrees[edge["to"]] = node_degrees.get(edge["to"], 0) + 1

    top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:10]

    context_parts.append("核心节点（连接数最多）：")
    for node_id, degree in top_nodes:
        node_name = next((n.get("label", node_id) for n in nodes if n.get("id") == node_id), node_id)
        context_parts.append(f"  - {node_name}: {degree} 个连接")

    return "\n".join(context_parts)


def query_graph(open_browser: bool = False) -> dict:
    """查询知识图谱

    返回图谱信息，供 OpenClaw LLM 综合生成回答

    Args:
        open_browser: 是否自动打开浏览器（默认 False）

    Returns:
        dict: {
            "html_path": "...",           # 图谱 HTML 文件路径（内部使用）
            "graph_data": {...},          # 图谱 JSON 数据
            "context": "...",             # 图谱描述上下文（供 LLM 使用）
            "opened": True/False,         # 是否成功打开浏览器
            "view_button": "...",        # 查看按钮 Markdown
        }
    """
    if not GRAPH_HTML.exists():
        return {
            "html_path": str(GRAPH_HTML),
            "graph_data": {},
            "context": "知识图谱尚未生成，请先执行 'build the knowledge graph'",
            "opened": False,
            "view_button": "",
        }

    html_path = str(GRAPH_HTML.resolve())

    # 读取图谱数据
    graph_data = read_graph_data()

    # 构建上下文
    context = build_graph_context(graph_data)

    # 尝试打开浏览器
    opened = False
    if open_browser:
        try:
            webbrowser.open(f"file://{html_path}")
            opened = True
        except Exception:
            pass

    # 生成查看按钮（不暴露完整路径）
    view_button = "<button style='background-color:#3370FF;color:white;padding:8px 16px;border-radius:4px;border:none;cursor:pointer;'>查看详情</button>"

    return {
        "html_path": html_path,
        "graph_data": graph_data,
        "context": context,
        "opened": opened,
        "view_button": view_button,
    }


def search_subgraph(keyword: str, hops: int = 1) -> dict:
    """按关键词搜索子图

    在节点 label 中模糊匹配关键词，提取匹配节点及其 N 跳邻居。

    Args:
        keyword: 搜索关键词
        hops: 邻居跳数（默认 1）

    Returns:
        dict: {
            "keyword": "...",
            "hops": 1,
            "matched_nodes": [...],   # 直接匹配的节点列表
            "nodes": [...],           # 子图所有节点（含邻居）
            "edges": [...],           # 子图所有边
            "context": "...",         # 子图描述文本
        }
    """
    graph_data = read_graph_data()
    if not graph_data:
        return {
            "keyword": keyword,
            "hops": hops,
            "matched_nodes": [],
            "nodes": [],
            "edges": [],
            "context": "知识图谱尚未生成。",
        }

    all_nodes = graph_data.get("nodes", [])
    all_edges = graph_data.get("edges", [])

    # 1. 查找直接匹配的节点（label 或 id 包含关键词）
    matched_ids = set()
    matched_nodes = []
    for node in all_nodes:
        label = node.get("label", "")
        node_id = node.get("id", "")
        text = f"{label} {node_id}"
        if keyword.lower() in text.lower():
            matched_ids.add(node_id)
            matched_nodes.append(node)

    if not matched_ids:
        return {
            "keyword": keyword,
            "hops": hops,
            "matched_nodes": [],
            "nodes": [],
            "edges": [],
            "context": f'未找到与 "{keyword}" 相关的节点。',
        }

    # 2. 扩展 N 跳邻居
    subgraph_node_ids = set(matched_ids)
    current_frontier = set(matched_ids)

    for _ in range(hops):
        next_frontier = set()
        for edge in all_edges:
            src = edge.get("from")
            dst = edge.get("to")
            if src in current_frontier and dst is not None:
                next_frontier.add(dst)
            if dst in current_frontier and src is not None:
                next_frontier.add(src)
        subgraph_node_ids.update(next_frontier)
        current_frontier = next_frontier

    # 3. 收集子图节点和边
    node_map = {n["id"]: n for n in all_nodes}
    subgraph_nodes = [node_map[nid] for nid in subgraph_node_ids if nid in node_map]
    subgraph_edges = [
        e for e in all_edges
        if e.get("from") in subgraph_node_ids and e.get("to") in subgraph_node_ids
    ]

    # 4. 构建上下文描述
    context_parts = []
    context_parts.append(f'关键词 "{keyword}" 子图搜索结果：')
    context_parts.append(f"- 直接匹配节点数：{len(matched_nodes)}")
    context_parts.append(f"- 子图总节点数：{len(subgraph_nodes)}")
    context_parts.append(f"- 子图边数：{len(subgraph_edges)}")
    context_parts.append("")
    context_parts.append("直接匹配节点：")
    for node in matched_nodes[:10]:
        context_parts.append(f"  - {node.get('label', node['id'])}（类型: {node.get('type', 'unknown')}）")
    if len(matched_nodes) > 10:
        context_parts.append(f"  ... 等共 {len(matched_nodes)} 个节点")

    # 邻居统计
    neighbor_count = len(subgraph_nodes) - len(matched_nodes)
    if neighbor_count > 0:
        context_parts.append(f"\n邻居节点数：{neighbor_count}")

    context = "\n".join(context_parts)

    return {
        "keyword": keyword,
        "hops": hops,
        "matched_nodes": matched_nodes,
        "nodes": subgraph_nodes,
        "edges": subgraph_edges,
        "context": context,
    }


def _generate_subgraph_html_template() -> str:
    """生成子图 HTML 模板（vis.js 自包含）"""
    return r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{title}} — Compass 子图</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  :root {
    --bg: #0f1117;
    --panel: rgba(18, 21, 30, 0.92);
    --text: #e8eaed;
    --muted: #9aa0a6;
    --accent: #ff6d3f;
    --accent2: #4fc3f7;
    --border: rgba(255,255,255,0.06);
    --chip-bg: rgba(255,255,255,0.07);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg);
    font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    color: var(--text); overflow: hidden;
  }
  #graph { width: 100vw; height: 100vh; }
  #controls {
    position: fixed; top: 14px; left: 14px;
    background: var(--panel); padding: 16px; border-radius: 14px;
    z-index: 10; max-width: 320px; min-width: 240px;
    backdrop-filter: blur(14px); border: 1px solid var(--border);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
  }
  #controls h3 { margin: 0 0 10px; font-size: 16px; letter-spacing: 0.3px; font-weight: 600; }
  #controls .meta { font-size: 12px; color: var(--muted); margin-bottom: 12px; line-height: 1.6; }
  #controls .meta span { color: var(--accent); font-weight: 600; }
  #search {
    width: 100%; padding: 8px 10px; margin-bottom: 10px;
    background: rgba(255,255,255,0.05); color: var(--text);
    border: 1px solid var(--border); border-radius: 8px; font-size: 13px;
    outline: none; transition: border-color 0.2s;
  }
  #search:focus { border-color: var(--accent); }
  #controls p { margin: 10px 0 0; font-size: 11px; color: var(--muted); line-height: 1.5; }
  .legend { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); }
  .legend-title { font-size: 11px; color: var(--muted); margin-bottom: 6px; }
  .legend-row { display: flex; align-items: center; gap: 6px; font-size: 11px; margin: 3px 0; }
  .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  #drawer {
    position: fixed; top: 0; right: 0;
    width: clamp(420px, 32vw, 640px); max-width: 100vw; height: 100vh;
    background: var(--panel); border-left: 1px solid var(--border);
    box-shadow: -20px 0 40px rgba(0,0,0,0.4); z-index: 20;
    display: none; flex-direction: column; backdrop-filter: blur(14px);
  }
  #drawer.open { display: flex; }
  #drawer-header {
    padding: 20px 20px 14px; border-bottom: 1px solid var(--border);
  }
  #drawer-topline {
    display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
  }
  #drawer-title { margin: 0; font-size: 20px; line-height: 1.25; font-weight: 600; }
  #drawer-close {
    background: transparent; color: var(--muted); border: 0; font-size: 24px;
    line-height: 1; cursor: pointer; padding: 0; transition: color 0.2s;
  }
  #drawer-close:hover { color: var(--text); }
  #drawer-meta { margin-top: 8px; font-size: 12px; color: var(--muted); }
  #drawer-path { margin-top: 6px; font-size: 12px; color: #5f6368; word-break: break-all; }
  #drawer-preview { margin-top: 12px; font-size: 13px; color: #d7d9e0; line-height: 1.6; }
  #drawer-related {
    padding: 14px 20px 0; font-size: 12px; color: var(--muted);
  }
  #drawer-related-list {
    display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;
  }
  .related-chip {
    background: var(--chip-bg); color: #f1f2f7;
    border: 1px solid var(--border); border-radius: 999px;
    font-size: 12px; padding: 5px 11px; cursor: pointer; transition: background 0.15s;
  }
  .related-chip:hover { background: rgba(255,255,255,0.12); }
  #drawer-content {
    flex: 1; min-height: 0; padding: 16px 20px 20px; overflow: auto;
  }
  #drawer-markdown {
    color: #e6e8ef; font-size: 13px; line-height: 1.72;
  }
  #drawer-markdown h1, #drawer-markdown h2, #drawer-markdown h3,
  #drawer-markdown h4, #drawer-markdown h5, #drawer-markdown h6 {
    margin: 1.2em 0 0.55em; line-height: 1.3; color: #fff;
  }
  #drawer-markdown h1 { font-size: 22px; }
  #drawer-markdown h2 { font-size: 18px; }
  #drawer-markdown h3 { font-size: 15px; }
  #drawer-markdown p { margin: 0 0 0.95em; }
  #drawer-markdown ul, #drawer-markdown ol { margin: 0 0 1em 1.35em; padding: 0; }
  #drawer-markdown li { margin: 0.35em 0; }
  #drawer-markdown hr { border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1.2em 0; }
  #drawer-markdown blockquote {
    margin: 0 0 1em; padding: 0.85em 1em;
    border-left: 3px solid rgba(101, 181, 255, 0.8);
    background: rgba(255,255,255,0.04); color: #d7d9e0; border-radius: 0 10px 10px 0;
  }
  #drawer-markdown pre {
    margin: 0 0 1em; white-space: pre-wrap; word-break: break-word; line-height: 1.55;
    background: rgba(255,255,255,0.04); padding: 10px 12px; border-radius: 8px;
    font-size: 12px; color: #c9cdd4;
  }
  #drawer-markdown code {
    background: rgba(255,255,255,0.08); padding: 2px 5px; border-radius: 4px;
    font-size: 12px; color: #ffab70;
  }
  #drawer-markdown table {
    border-collapse: collapse; width: 100%; margin: 0 0 1em; font-size: 12px;
  }
  #drawer-markdown th, #drawer-markdown td {
    border: 1px solid rgba(255,255,255,0.1); padding: 6px 8px; text-align: left;
  }
  #drawer-markdown th { background: rgba(255,255,255,0.06); font-weight: 600; }
  .toast {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    background: var(--panel); color: var(--text); padding: 10px 18px;
    border-radius: 10px; font-size: 13px; z-index: 50;
    border: 1px solid var(--border); opacity: 0; pointer-events: none;
    transition: opacity 0.3s;
  }
  .toast.show { opacity: 1; }
</style>
</head>
<body>
<div id="graph"></div>

<div id="controls">
  <h3>{{title}}</h3>
  <div class="meta">
    节点 <span>{{node_count}}</span> · 边 <span>{{edge_count}}</span><br>
    关键词 <span style="color:var(--accent2)">{{keyword}}</span> · {{hops}} 跳邻居
  </div>
  <input id="search" type="text" placeholder="搜索节点..." />
  <p>点击节点查看详情 · 滚轮缩放 · 拖拽画布</p>
  <div class="legend">
    <div class="legend-title">节点类型</div>
    {{legend_items}}
  </div>
</div>

<div id="drawer">
  <div id="drawer-header">
    <div id="drawer-topline">
      <h3 id="drawer-title"></h3>
      <button id="drawer-close">&times;</button>
    </div>
    <div id="drawer-meta"></div>
    <div id="drawer-path"></div>
    <div id="drawer-preview"></div>
    <div id="drawer-related">
      关联节点
      <div id="drawer-related-list"></div>
    </div>
  </div>
  <div id="drawer-content">
    <div id="drawer-markdown"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const graphData = {{graph_data_json}};
const matchedNodeIds = new Set({{matched_node_ids_json}});

// 节点类型颜色映射
const typeColorMap = {};
graphData.nodes.forEach(n => {
  const t = n.type || 'unknown';
  if (!typeColorMap[t]) typeColorMap[t] = n.color || '#9E9E9E';
});

const nodes = new vis.DataSet(graphData.nodes.map(n => ({
  id: n.id,
  label: n.label || n.id,
  title: n.type ? `${n.type}: ${n.label || n.id}` : (n.label || n.id),
  color: {
    background: n.color || '#9E9E9E',
    border: matchedNodeIds.has(n.id) ? '#ff6d3f' : (n.color || '#9E9E9E'),
    highlight: { background: '#ff6d3f', border: '#ff6d3f' },
    hover: { background: '#ff8a65', border: '#ff8a65' }
  },
  borderWidth: matchedNodeIds.has(n.id) ? 3 : 1,
  borderWidthSelected: 4,
  font: { color: '#e8eaed', size: 13, face: 'Noto Sans SC, PingFang SC, Microsoft YaHei' },
  shape: n.type === 'person' ? 'dot' : (n.type === 'project' ? 'hexagon' : 'dot'),
  size: matchedNodeIds.has(n.id) ? 22 : (n.value ? Math.min(30, 10 + n.value * 1.5) : 14),
  shadow: matchedNodeIds.has(n.id) ? { enabled: true, color: 'rgba(255,109,63,0.5)', size: 12 } : { enabled: false },
  ...n
})));

const edges = new vis.DataSet(graphData.edges.map(e => ({
  from: e.from,
  to: e.to,
  label: e.label || '',
  title: e.type || '',
  color: { color: e.color || 'rgba(255,255,255,0.15)', highlight: '#ff6d3f', hover: '#4fc3f7' },
  width: 1,
  arrows: { to: { enabled: true, scaleFactor: 0.6 } },
  smooth: { type: 'continuous' },
  ...e
})));

const container = document.getElementById('graph');
const data = { nodes, edges };
const options = {
  nodes: {
    borderWidth: 1,
    font: { color: '#e8eaed' },
  },
  edges: {
    color: { inherit: false },
    smooth: { type: 'continuous', roundness: 0.2 },
  },
  physics: {
    forceAtlas2Based: {
      gravitationalConstant: -60,
      centralGravity: 0.005,
      springLength: 160,
      springConstant: 0.05,
      damping: 0.4,
    },
    maxVelocity: 80,
    solver: 'forceAtlas2Based',
    timestep: 0.35,
    stabilization: { iterations: 120, updateInterval: 25 },
  },
  interaction: {
    hover: true,
    tooltipDelay: 200,
    hideEdgesOnDrag: true,
    navigationButtons: true,
    keyboard: true,
  },
};

const network = new vis.Network(container, data, options);

// 搜索高亮
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', (e) => {
  const val = e.target.value.trim().toLowerCase();
  if (!val) { network.unselectAll(); return; }
  const found = graphData.nodes.filter(n => (n.label || n.id).toLowerCase().includes(val));
  if (found.length) {
    network.selectNodes(found.map(n => n.id));
    network.focus(found[0].id, { scale: 1.2, animation: true });
  }
});

// Drawer
const drawer = document.getElementById('drawer');
const drawerTitle = document.getElementById('drawer-title');
const drawerMeta = document.getElementById('drawer-meta');
const drawerPath = document.getElementById('drawer-path');
const drawerPreview = document.getElementById('drawer-preview');
const drawerRelated = document.getElementById('drawer-related-list');
const drawerMarkdown = document.getElementById('drawer-markdown');
const drawerClose = document.getElementById('drawer-close');

drawerClose.addEventListener('click', () => drawer.classList.remove('open'));

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function mdToHtml(md) {
  if (!md) return '';
  let html = escapeHtml(md);
  html = html.replace(/^#{6}\s+(.*)$/gm, '<h6>$1</h6>');
  html = html.replace(/^#{5}\s+(.*)$/gm, '<h5>$1</h5>');
  html = html.replace(/^#{4}\s+(.*)$/gm, '<h4>$1</h4>');
  html = html.replace(/^#{3}\s+(.*)$/gm, '<h3>$1</h3>');
  html = html.replace(/^#{2}\s+(.*)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#{1}\s+(.*)$/gm, '<h1>$1</h1>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  html = html.replace(/^\s*[-*]\s+(.*)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
  html = html.replace(/\n/g, '<br>');
  return html;
}

network.on('click', (params) => {
  if (params.nodes.length === 0) {
    drawer.classList.remove('open');
    return;
  }
  const nodeId = params.nodes[0];
  const node = graphData.nodes.find(n => n.id === nodeId);
  if (!node) return;

  drawerTitle.textContent = node.label || node.id;
  drawerMeta.textContent = `类型: ${node.type || 'unknown'}${node.value ? ' · 权重: ' + node.value : ''}`;
  drawerPath.textContent = node.path || '';
  drawerPreview.textContent = node.preview ? (node.preview.slice(0, 280) + (node.preview.length > 280 ? '...' : '')) : '';
  drawerMarkdown.innerHTML = node.markdown ? mdToHtml(node.markdown) : '<p style="color:#5f6368">无详细内容</p>';

  // 关联节点
  const related = graphData.edges
    .filter(e => e.from === nodeId || e.to === nodeId)
    .map(e => {
      const rid = e.from === nodeId ? e.to : e.from;
      const rnode = graphData.nodes.find(n => n.id === rid);
      return rnode ? { id: rid, label: rnode.label || rid, type: e.type || '关联' } : null;
    })
    .filter(Boolean);

  const seen = new Set();
  const uniqueRelated = [];
  related.forEach(r => { if (!seen.has(r.id)) { seen.add(r.id); uniqueRelated.push(r); } });

  drawerRelated.innerHTML = '';
  if (uniqueRelated.length === 0) {
    drawerRelated.innerHTML = '<span style="color:#5f6368">无关联节点</span>';
  } else {
    uniqueRelated.slice(0, 20).forEach(r => {
      const chip = document.createElement('span');
      chip.className = 'related-chip';
      chip.textContent = r.label;
      chip.title = r.type;
      chip.addEventListener('click', () => {
        network.selectNodes([r.id]);
        network.focus(r.id, { scale: 1.3, animation: true });
      });
      drawerRelated.appendChild(chip);
    });
  }

  drawer.classList.add('open');
});

// 初始聚焦到第一个匹配节点
const firstMatched = graphData.nodes.find(n => matchedNodeIds.has(n.id));
if (firstMatched) {
  setTimeout(() => {
    network.selectNodes([firstMatched.id]);
    network.focus(firstMatched.id, { scale: 1.2, animation: true });
  }, 800);
}
</script>
</body>
</html>
'''


def generate_subgraph_html(subgraph_result: dict, output_path: Optional[Union[str, Path]] = None) -> str:
    """生成子图自包含 HTML 文件

    Args:
        subgraph_result: search_subgraph() 的返回值
        output_path: 输出 HTML 路径（默认 workspace/knowledge/graph/subgraph_{keyword}.html）

    Returns:
        str: 生成的 HTML 文件绝对路径
    """
    keyword = subgraph_result.get("keyword", "subgraph")
    hops = subgraph_result.get("hops", 1)
    nodes = subgraph_result.get("nodes", [])
    edges = subgraph_result.get("edges", [])
    matched_nodes = subgraph_result.get("matched_nodes", [])

    if output_path is None:
        safe_kw = "".join(c if c.isalnum() or c in "-_" else "_" for c in keyword)[:30]
        output_path = REPO_ROOT / "workspace" / "knowledge" / "graph" / f"subgraph_{safe_kw}.html"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 收集节点类型用于图例
    type_colors = {}
    for node in nodes:
        t = node.get("type", "unknown")
        if t not in type_colors:
            type_colors[t] = node.get("color", "#9E9E9E")

    legend_items = "\n".join(
        f'<div class="legend-row"><span class="dot" style="background:{color}"></span> {t}</div>'
        for t, color in sorted(type_colors.items())
    )

    matched_ids = [n["id"] for n in matched_nodes]

    template = _generate_subgraph_html_template()
    html = template.replace("{{title}}", f"子图: {keyword}")
    html = html.replace("{{node_count}}", str(len(nodes)))
    html = html.replace("{{edge_count}}", str(len(edges)))
    html = html.replace("{{keyword}}", keyword)
    html = html.replace("{{hops}}", str(hops))
    html = html.replace("{{legend_items}}", legend_items)
    html = html.replace("{{graph_data_json}}", json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False))
    html = html.replace("{{matched_node_ids_json}}", json.dumps(matched_ids, ensure_ascii=False))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return str(output_path.resolve())


def serve_html(html_path: str, port: int = 8765) -> None:
    """启动本地 HTTP 服务器，提供图谱 HTML 访问

    Args:
        html_path: 要服务的 HTML 文件路径
        port: 服务端口（默认 8765）
    """
    html_path = Path(html_path).resolve()
    serve_dir = html_path.parent
    target_file = html_path.name

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(serve_dir), **kwargs)

        def do_GET(self):
            if self.path == '/':
                self.path = f'/{target_file}'
            return super().do_GET()

        def log_message(self, format, *args):
            # 精简日志输出
            pass

    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"\n  HTTP 服务已启动: {url}")
        print(f"  正在服务: {html_path}")
        print(f"  按 Ctrl+C 停止服务\n")

        # 尝试自动打开浏览器
        try:
            webbrowser.open(url)
            print("  已自动打开浏览器")
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  服务已停止")


def describe_graph() -> str:
    """返回图谱纯文本描述（供 LLM 使用）"""
    graph_data = read_graph_data()
    return build_graph_context(graph_data)


def main():
    parser = argparse.ArgumentParser(description="Query Compass graph (retrieval + subgraph + serve)")
    parser.add_argument("keyword", nargs="?", default=None, help="关键词子图搜索（如: 垂类达人孵化）")
    parser.add_argument("--open", action="store_true", help="打开浏览器（查看完整图谱）")
    parser.add_argument("--json", action="store_true", help="输出为 JSON")
    parser.add_argument("--serve", action="store_true", help="启动本地 HTTP 服务")
    parser.add_argument("--port", type=int, default=8765, help="HTTP 服务端口（默认 8765）")
    parser.add_argument("--hops", type=int, default=1, help="子图邻居跳数（默认 1）")
    parser.add_argument("--output", type=str, default=None, help="子图 HTML 输出路径")
    args = parser.parse_args()

    # 模式 1: 关键词子图搜索
    if args.keyword:
        subgraph = search_subgraph(args.keyword, hops=args.hops)

        if args.json:
            json_result = {
                "keyword": subgraph["keyword"],
                "hops": subgraph["hops"],
                "context": subgraph["context"],
                "node_count": len(subgraph["nodes"]),
                "edge_count": len(subgraph["edges"]),
                "matched_count": len(subgraph["matched_nodes"]),
            }
            print(json.dumps(json_result, ensure_ascii=False, indent=2))
        else:
            print("=" * 60)
            print(f"子图搜索: {args.keyword}")
            print("=" * 60)
            print(subgraph["context"])

        if not subgraph["nodes"]:
            sys.exit(1)

        # 生成子图 HTML
        html_path = generate_subgraph_html(subgraph, output_path=args.output)
        print(f"\n  子图 HTML 已生成: {html_path}")

        if args.serve:
            serve_html(html_path, port=args.port)
        elif not args.json:
            print(f"\n  用以下命令启动服务查看:")
            print(f"  python tools/graph_query.py \"{args.keyword}\" --serve")

        return

    # 模式 2: 完整图谱查询
    result = query_graph(open_browser=args.open)

    if args.json:
        json_result = {
            "context": result["context"],
            "view_button": result["view_button"],
            "opened": result["opened"],
        }
        print(json.dumps(json_result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("知识图谱查询结果")
        print("=" * 60)
        print(result["context"])
        if result["view_button"]:
            print(f"\n{result['view_button']}")

    if args.serve and result["html_path"] and Path(result["html_path"]).exists():
        serve_html(result["html_path"], port=args.port)


if __name__ == "__main__":
    main()
