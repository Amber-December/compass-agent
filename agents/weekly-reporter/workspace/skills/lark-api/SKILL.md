---
name: lark-api
description: "飞书 Lark API 基础能力封装，统一调用规范与错误处理"
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
      },
  }
---

# lark-api Skill

> 飞书 Lark API 基础能力封装，统一调用规范与错误处理

## 归属

- **Agent**: weekly-reporter
- **路径**: `agents/weekly-reporter/workspace/skills/lark-api/`

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

### 身份选择原则

- `--as user`：访问用户资源（日历、云空间、个人文档）
- `--as bot`：应用级操作，访问 bot 自己的资源

### 权限不足处理

1. 检查错误中的 `permission_violations` 字段，获取缺失的 scope
2. 将 `console_url` 提供给用户，引导去后台开通 scope
