# 周报合成助手 (weekly-reporter)

负责每周一早晨自动合成项目周报和部门看板。

## 职责

- 📊 从 Base/妙记/Wiki 采集上周数据
- 📝 按场景配置生成项目级周报
- 📋 汇总多个项目生成部门看板
- 💬 推送飞书消息卡片到项目群和部门群

## 触发方式

- 定时触发：每周一 9:00（cron）
- 人工指令："生成本周周报"

## 输入输出

| 输入 | 输出 |
|------|------|
| Base 上周数据 | 项目周报 Markdown |
| 妙记会议要点 | 部门看板卡片 |
| Wiki 本周更新 | 周报飞书文档 |

## 依赖

- `shared/skills/lark-api`
- `shared/skills/data-collection`
- `shared/skills/prompt-template`
- `shared/skills/card-builder`
- `shared/skills/llm-wiki-builder`
- 配置文件：`config/scenarios/mcn.yaml`
