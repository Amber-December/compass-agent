# 效能分析助手 (efficiency-analyzer)

负责团队效能数据的采集、分析、洞察生成和卡片推送。

## 职责

- 📊 从飞书各模块采集效能数据
- 📈 计算效能指标（完成率、逾期率、文档活跃度等）
- 💡 生成数据洞察和趋势判断
- 📨 构建并推送效能分析卡片

## 触发方式

- 定时触发：每日/每周心跳检查
- 人工指令："查看本周效能"

## 输入输出

| 输入 | 输出 |
|------|------|
| 飞书任务/日程/文档数据 | 效能分析卡片 |
| 历史对比数据 | 趋势洞察报告 |

## 依赖

- `shared/skills/lark-api`
- `shared/skills/data-collection`
- `shared/skills/analytics`
- `shared/skills/insight-llm`
- `shared/skills/card-builder`
- `shared/skills/threshold-check`
