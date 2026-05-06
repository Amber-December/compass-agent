---
name: wiki-read
description: "wiki-read"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 读取飞书 Wiki 知识库文档内容，获取节点结构与文档 Markdown

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/wiki-read/`

## 能力

- 获取 Wiki 空间/节点信息
- 读取文档内容（转为 Markdown）
- 批量导出知识库为本地 Markdown 文件

## 使用方法

### 获取节点信息

```bash
lark-cli wiki spaces get_node --params '{"token":"wiki_token"}'
```

返回关键字段：
- `obj_token`: 真实文档 token
- `obj_type`: 文档类型（docx/doc/sheet/bitable）
- `title`: 文档标题
- `space_id`: 知识空间 ID

### 读取文档内容

```bash
lark-cli docs +fetch --doc <obj_token> --format pretty
```

### 批量导出

```bash
# 先列出空间下所有节点
lark-cli wiki nodes list --params '{"space_id":"space_id"}'

# 再逐个读取
```

## 注意事项

- Wiki 链接中的 token 是 wiki_token，不是文档 token，必须先查询
- 需要权限：`wiki:node:read`、`docx:document:readonly`
