# 消息卡片模板

本目录存放飞书消息卡片的 JSON 模板，用于周报、看板、预警的推送。

## 卡片类型

| 模板 | 说明 | 状态 |
|------|------|------|
| weekly-report.json | 项目周报卡片 | 待创建 |
| dept-board.json | 部门看板卡片 | 待创建 |
| risk-alert.json | 风险预警卡片 | 待创建 |
| qa-answer.json | Q&A 回答卡片 | 待创建 |

## 卡片规范

- 使用飞书 Message Card 格式（interactive 类型）
- 配置 `wide_screen_mode: true`
- 使用 emoji 和颜色增强可读性
- 关键数据加粗显示
- 包含跳转到详细文档的按钮
