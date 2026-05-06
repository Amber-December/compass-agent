---
name: lark-api
description: "lark-api"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---


> 飞书 Lark API 基础能力封装，统一调用规范与错误处理

## 归属

- **Agent**: wiki-manager
- **路径**: `agents/wiki-manager/workspace/skills/lark-api/`

## 能力

- 统一调用 `lark-cli` 进行 API 请求
- 身份切换（`--as user` / `--as bot`）
- 错误处理与权限诊断
- 分页查询自动处理

## 通用调用模式

```bash
lark-cli <resource> <method> [flags]
```

常用 flags：
- `--as user|bot` — 切换身份
- `--params '{"key":"value"}'` — URL 查询参数
- `--data '{"key":"value"}'` — POST 请求体
- `--format json|pretty` — 输出格式

### 查看 API 参数结构

```bash
lark-cli schema <resource>.<method>
```

### 身份选择原则

- `--as user`：访问用户资源（日历、云空间、个人文档）
- `--as bot`：应用级操作，访问 bot 自己的资源
- Bot 看不到用户资源，无法代表用户操作

### 权限不足处理

1. 检查错误中的 `permission_violations` 字段，获取缺失的 scope
2. User 身份：`lark-cli auth login --scope "<missing_scope>"`
3. Bot 身份：将 `console_url` 提供给用户，引导去后台开通 scope

## 常用 API 速查

| 操作 | 命令 |
|------|------|
| 获取 Wiki 节点 | `lark-cli wiki spaces get_node --params '{"token":"xxx"}'` |
| 创建 Wiki 节点 | `lark-cli wiki +node-create --space xxx --parent xxx --type docx --title xxx` |
| 读取文档 | `lark-cli docs +fetch --doc <obj_token>` |
| 创建文档 | `lark-cli docs +create --title xxx --content xxx` |
| 拉取 Base 数据 | `lark-cli base records list --params '{"app_token":"xxx"}'` |
| 发送群消息 | `lark-cli im messages create --data '{"receive_id":"xxx","msg_type":"text","content":"{}"}'` |
| 搜索用户 | `lark-cli contact +search-user --query "xxx"` |
