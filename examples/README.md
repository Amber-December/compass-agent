# Compass 示例数据

本目录包含 Compass（司南）项目的**模拟/示范数据**，供开发者快速了解系统结构和数据格式。

> **注意**：以下所有数据均为虚构的演示数据，不含任何真实业务信息。你可以直接使用这些数据进行本地开发、测试和体验。

---

## 目录结构

```
examples/
├── README.md                 # 本文件
├── base/                     # 飞书 Base 多维表格数据快照（JSON）
└── wiki/                     # 飞书 Wiki 文档原始 Markdown
```

---

## base/

模拟从飞书 Base 同步的多维表格数据，按项目分类存储为 JSON 文件。

| 项目 | 数据表 |
|---|---|
| `kol-incubation/` | 达人档案、达人周度快照、内容产出、品牌合作、团队档案、项目周度KPI |
| `brand-ops/` | 客户档案、客户周度快照、服务记录、团队档案、项目周度KPI |
| `live-commerce/` | 主播档案、主播周度快照、直播场次、选品管理、团队档案、项目周度KPI |
| `short-video/` | 账号档案、账号周度快照、内容产出、团队档案、项目周度KPI |
| `private-domain/` | 社群档案、社群周度快照、成员档案、活动记录、团队档案、项目周度KPI |
| `virtual-ip/` | IP档案、IP周度快照、直播场次、技术故障、数据表、团队档案、项目周度KPI |
| `mcn/` | 部门健康度周报、项目清单、项目周度KPI汇总 |

每个数据表通常包含：
- `{table_name}.json` — 实际数据（数组格式）
- `{table_name}_meta.json` — 元数据（字段类型、枚举值等）

### 示例数据预览

```json
[
  {
    "总GMV": 337500,
    "直播转化率": 0.038,
    "场均观看": 9000,
    "ROI": 2,
    "总订单数": 1368,
    "项目状态": "正常",
    "周次": 1,
    "日期范围": "2026-03-09 至 2026-03-15"
  }
]
```

---

## wiki/

模拟从飞书 Wiki 同步的原始 Markdown 文档，保留了 frontmatter 元数据。

| 目录 | 内容 |
|---|---|
| `public/` | 公共文档：入职指南、SOP、培训资料、工具使用说明 |
| `dept/` | 部门级文档：部门周报、部门 OnePage、项目汇总 |
| `projects/{project}/` | 项目文档：周报、会议纪要、项目 OnePage、SOP |

### 示例文档结构

```markdown
---
title: 入职指南
doc_type: default
scope: public
lark_url: https://example.feishu.cn/wiki/FSs4wR8y9iefVwkWZarcfmqWnRh
lark_node_id: FSs4wR8y9iefVwkWZarcfmqWnRh
content_hash: 01ba4719c80b6fe9
fetched_at: '2026-05-07T03:24:24.699186'
status: active
---

# 入职指南

欢迎加入 MCN 事业部...
```

### 可用项目

- `kol-incubation` — 垂类达人孵化
- `brand-ops` — 品牌代运营
- `live-commerce` — 直播电商
- `short-video` — 短视频内容矩阵
- `private-domain` — 达人私域运营
- `virtual-ip` — 虚拟IP孵化

---

## 如何使用

### 1. 直接放入 raw_lark 体验（推荐）

wiki-manager 的同步目标目录 `agents/wiki-manager/workspace/raw_lark/` 保持与飞书侧一致的 `base/minutes/wiki` 结构。你可以直接将示例数据复制进去，无需连接真实飞书即可体验完整流程：

```bash
# 将示例 Wiki 文档放入 raw_lark
cp -R examples/wiki/* agents/wiki-manager/workspace/raw_lark/wiki/

# 将示例 Base 数据放入 knowledge/data
cp -R examples/base/* workspace/knowledge/data/

# 然后运行 wiki-ingest 编译知识底座
python agents/wiki-manager/workspace/tools/wiki_ingest.py
```

### 2. 快速体验数据查询

```python
import json

with open('examples/base/live-commerce/project_kpi.json') as f:
    data = json.load(f)
    print(f"共 {len(data)} 周数据")
    print(f"平均 GMV: {sum(d['总GMV'] for d in data) / len(data):,.0f}")
```

### 3. 运行 wiki-ingest 编译知识底座

将 `examples/wiki/` 作为输入，运行 wiki-manager 的知识编译流程，即可生成：
- `wiki/concepts/` — 概念页
- `wiki/entities/` — 实体页
- `wiki/index.md` — 知识库索引
- `wiki/overview.md` — 综合认知

### 4. 构建知识图谱

基于编译后的 wiki 内容，运行 `build_graph.py` 生成 `graph.json` 和可视化 HTML。

---

## 数据生成说明

- 所有数值（GMV、ROI、转化率等）均为随机生成的演示数据
- 人名、品牌名、项目代号均为虚构
- 日期范围设定在 2026 年 3 月至 5 月，仅用于演示时间序列分析
- 文档内容使用 LLM 生成的示范文本

---

## 许可证

本示例数据与 Compass 项目主体使用相同许可证，可自由用于开发、测试和学习目的。
