# 风险检测助手 (risk-monitor)

负责根据场景配置的阈值和规则，检测项目风险并生成嵌入式预警。

## 职责

- 🔍 扫描 Base 中的 KPI 数据，对比预设阈值
- 📝 从妙记/群消息中提取风险关键词
- 🧠 LLM 综合判断是否为真实风险
- ⚠️ 将风险信息嵌入到周报中

## 触发方式

- 定时触发：每周一 9:00（与周报一起生成）
- 嵌入式：作为周报合成的一个环节

## 输入输出

| 输入 | 输出 |
|------|------|
| KPI 数据 | 风险等级判断 |
| 妙记/消息文本 | 风险原因说明 |
| 场景阈值配置 | 嵌入周报的风险段落 |

## 依赖

- `shared/skills/lark-api`
- `shared/skills/data-collection`
- `shared/skills/threshold-check`
- `shared/skills/prompt-template`
- 配置文件：`config/scenarios/mcn.yaml` 中的 thresholds 部分
