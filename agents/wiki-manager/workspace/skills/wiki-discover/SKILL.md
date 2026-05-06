---
name: wiki-discover
description: "wiki-discover"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 飞书 Wiki 空间自动扫描 — 发现新增/变更/缺失的文档节点，更新 sources.yaml 注册表

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/wiki-discover/`

## 触发条件

- **自动**：`workflow.json` 中作为 `step-0`，在每次 wiki-sync 之前自动执行
  - 每周一 8:30 全量同步前
  - 用户手动触发 "刷新知识库" 时
- **手动**：运行 `python tools/wiki_discover.py`（在 workspace 目录下）

## 核心能力

### 1. 递归扫描 Wiki 空间

通过 `lark-cli wiki nodes list` 递归遍历空间内所有节点：
- **有子节点（`has_child=true`）的节点**：展开其子节点（飞书 Wiki 中 folder 本身也是 docx，用 `has_child` 判断）
- **docx 节点**：收集 node_token、obj_token、title、parent 链
- **其他类型**（sheet、bitable 等）：忽略，由 base-sync 或手动配置管理
- **分页与去重**：支持 API 分页翻页，已访问 token 集合防止循环引用和重复扫描

### 2. 构建完整路径

通过 parent_node_token 链回溯，构建每个 docx 节点的完整路径：
```
4 项目管理 / 垂类达人孵化 / 周报归档 / Week 9 周报
```

### 3. 对比与推断

与 `sources.yaml` 中现有 `wiki.nodes` 对比：

| 情况 | 处理 |
|------|------|
| 飞书有、yaml 无 | **自动 append** 到 sources.yaml |
| 飞书有、yaml 有、title 不同 | **自动更新** title |
| 飞书有、yaml 有、obj_token 不同 | **自动更新** obj_token |
| 飞书有、yaml 有、路径漂移 | **自动更新** scope / project_id |
| 飞书无、yaml 有 | **只输出告警**，不修改 yaml |

### 4. Scope 自动推断

新增节点按 `scope_rules` 路径匹配自动推断：
```yaml
scope_rules:
  - path: "垂类达人孵化/*"
    scope: "projects"
    project_id: "kol-incubation"
```

匹配逻辑（按优先级）：
1. **精确匹配**：路径中某一段完整等于 pattern（去 `*` 后）
2. **前缀匹配**：路径中某一段以 pattern 开头（如 `虚拟IP孵化` 匹配 `虚拟IP孵化与运营`）

已有明确 scope 的节点不会被降级覆盖为 `pending`；无法匹配的新增节点标为 `scope: pending`，但不阻断同步 pipeline。

### 5. 报告生成

输出 `state/discover_report.json`，包含：
- added / updated / missing / unchanged 统计
- 每个新增节点的完整路径和推断的 scope
- 每个变更节点的 diff

## 执行步骤

1. 读取 `sources.yaml`，提取 space_id、scope_rules、现有 nodes
2. 递归调用 `lark-cli wiki nodes list` 扫描整个 Wiki 空间
3. 筛选 docx 节点，构建路径映射
4. 与现有 nodes 对比，识别新增、变更、缺失
5. 对新增节点按 scope_rules 推断 scope 和 project_id
6. 更新 `sources.yaml`（append 新增、修改变更字段）
7. 写入 discover_report
8. 打印变更摘要

## 与 wiki-sync 的关系

```
wiki-discover（step-0：更新 sources.yaml 注册表）
    └── wiki-sync（step-1：基于最新注册表拉取文档）
        └── wiki-ingest（step-3：编译）
```

- discover **不直接拉取文档内容**，只维护 "哪些文档应该被同步" 的注册表
- wiki-sync 基于最新的 sources.yaml 执行实际的 fetch + hash 对比
- 两者解耦：discover 负责 "发现范围"，sync 负责 "内容同步"

## 参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `--dry-run` | 预览变更，不写入 sources.yaml | false |
| `--report` | 生成 `state/discover_report.json` | false |

## 红线

- **绝不删除 yaml 中的节点**：即使飞书侧已删除，也只在报告中告警，由 wiki_sync.py 在 fetch 失败时被动标记 archived
- **只处理 docx**：bitable / sheet 节点不纳入自动发现
- **folder 不注册**：folder 只用于递归展开，不写入 sources.yaml
- **备份原文件**：修改前先写 `.sources.yaml.bak`
