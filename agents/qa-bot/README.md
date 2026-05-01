# 自然查询助手 (qa-bot)

负责接收群内 @ 消息，基于本地 LLM-Wiki 进行知识问答。

## 职责

- 💬 接收并理解群内 @ 消息
- 🎯 识别查询意图（数据/知识/跨项目/边界外推）
- 🛡️ 判断是否需要拒答（敏感数据）
- 🔍 从本地知识底座检索相关内容
- 💡 生成带飞书链接引用的准确答案

## 触发方式

- 事件触发：群内被 @ 提及（lark-event WebSocket）

## 输入输出

| 输入 | 输出 |
|------|------|
| @消息文本 | Markdown 答案 |
| 项目 scope | 飞书链接引用 |

## 拒答规则

以下情况必须拒答：
- 其他项目的 KPI 具体数值
- 其他项目的达人个人绩效、违规记录
- 其他项目的整改进度细节
- 数据外的外推/预测

拒答话术：
```
"⚠️ 跨项目敏感数据未开放，如需详情请到 [项目名] 群内询问。"
```

## 依赖

- `shared/skills/lark-api`
- `shared/skills/llm-wiki-builder`
- `shared/skills/prompt-template`
- `shared/skills/intent-classifier`
