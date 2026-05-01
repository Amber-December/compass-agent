# Wiki 推送操作指南

## 任务
将本地 `docs/MCN lark/` 目录下的 Markdown 文档推送到指定的飞书 Wiki 知识库中。

## 本地文档清单

| 序号 | 文件名 | 标题 | 说明 |
|------|--------|------|------|
| 0 | `0 知识库使用说明.md` | 知识库使用说明 | 知识空间目录说明、权限管理 |
| 1 | `1 MCN 部门使用说明` | MCN 部门使用说明 | 部门架构、项目一览、工作节奏 |
| 2 | `2 团队建设与培训` | 团队建设与培训 | 新人上手、培训材料、学习资源 |
| 3 | `3 流程制度规范.md` | 流程制度规范 | 达人管理、内容审核、商务合作、私域运营 |
| 4 | `4 项目管理.md` | 项目管理 | 项目列表、OnePage 模板、周报模板、复盘模板 |

## 操作步骤

### Step 1: 确认目标 Wiki 空间

获取目标空间的 `space_id` 和父节点 `node_token`：

```bash
# 列出用户可访问的 wiki 空间
lark-cli wiki spaces list --as user

# 或获取指定节点信息
lark-cli wiki spaces get_node --as user --params '{"token":"C5frwx9GUi14OSkIPiScKtegnud"}'
```

### Step 2: 创建一级目录节点（如果不存在）

在目标空间下创建 "MCN 部门知识库" 根节点：

```bash
lark-cli wiki +node-create --space <space_id> --parent <root_node_token> --type docx --title "MCN 部门知识库"
```

### Step 3: 批量推送文档

使用脚本一键推送：

```bash
cd /Users/amber/lark-knowledge-agent
python scripts/wiki_push.py --space <space_id> --parent <mcn_root_node_token> --dir "docs/MCN lark"
```

或手动逐个创建：

```bash
# 创建文档并获取 obj_token
lark-cli docx documents create --data '{"title":"知识库使用说明"}'

# 写入内容（通过 blocks API）
lark-cli docx documents blocks create --params '{"document_id":"<obj_token>"}' --data '{"children":[...]}'

# 挂载到 Wiki
lark-cli wiki nodes create --data '{"space_id":"<space_id>","parent_node_token":"<mcn_root>","obj_type":"docx","obj_token":"<obj_token>","title":"知识库使用说明"}'
```

### Step 4: 验证

推送完成后，在飞书 Wiki 中检查：
- 5 个文档是否都在 "MCN 部门知识库" 节点下
- 文档内容是否完整
- 目录层级是否正确

## 权限要求

需要开通以下 scope：
- `wiki:space:read` — 读取空间信息
- `wiki:node:read` — 读取节点信息
- `wiki:node:create` — 创建节点
- `docx:document:write` — 创建/编辑文档

## 常见问题

**Q: 推送失败，提示权限不足？**
A: 检查当前身份（`--as user` 或 `--as bot`），确保应用已被添加到 Wiki 空间成员中。

**Q: 文档内容格式错乱？**
A: 当前脚本使用简化的 Markdown 转 block 逻辑，复杂表格和样式可能无法完全保留。推送后可在飞书中手动微调。

**Q: 需要更新已推送的文档？**
A: 使用 `lark-cli docx documents blocks batch_update` 更新内容，或删除旧节点重新推送。
