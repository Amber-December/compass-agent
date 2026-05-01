# card-builder

飞书消息卡片构建能力，用于周报、看板、预警的格式化推送。

## 能力

- 构建飞书交互卡片（Message Card）
- 支持 Markdown、图片、按钮、分割线等组件
- 支持颜色标记（红/黄/绿状态）

## 卡片模板

### 项目周报卡片

```json
{
  "config": { "wide_screen_mode": true },
  "elements": [
    { "tag": "div", "text": { "tag": "lark_md", "content": "**📊 司南 · 上周战报 — [项目名]**" } },
    { "tag": "div", "text": { "tag": "lark_md", "content": "👤 [指标说明]\n📈 [数据对比]\n💰 [核心 KPI]\n✅ [任务完成]\n⚠️ [风险点]\n🎯 [本周计划]" } },
    { "tag": "action", "actions": [{ "tag": "button", "text": { "tag": "plain_text", "content": "查看完整周报" }, "type": "primary", "url": "[文档链接]" }] }
  ]
}
```

### 部门看板卡片

```json
{
  "config": { "wide_screen_mode": true },
  "elements": [
    { "tag": "div", "text": { "tag": "lark_md", "content": "**📌 司南 · 部门看板 — MCN 事业部**" } },
    { "tag": "div", "text": { "tag": "lark_md", "content": "6 个项目: 🟢 4  🟡 1  🔴 1\n🔴 [风险项目]\n🟡 [预警项目]" } },
    { "tag": "div", "text": { "tag": "lark_md", "content": "📚 本周精选:\n1. [精选1]\n2. [精选2]\n3. [精选3]" } }
  ]
}
```

## 使用方式

通过 `lark-cli im messages create` 发送卡片：
```bash
lark-cli im messages create --data '{
  "receive_id": "chat_id",
  "msg_type": "interactive",
  "content": "{\"card\": {...}}"
}'
```
