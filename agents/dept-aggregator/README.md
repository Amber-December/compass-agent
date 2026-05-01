# 部门聚合助手 (dept-aggregator)

负责聚合多项目周报、生成部门看板、评选 Top3 知识精选。

## 职责

- 🚦 汇总各项目状态（🟢🟡🔴）
- 📈 生成部门级 KPI 看板
- ⭐ 自动评选本周 Top3 知识精选
- 📨 推送部门看板卡片到部门群

## 触发方式

- 定时触发：每周一 9:05（在周报推送后）
- 人工指令："生成部门看板"

## 输入输出

| 输入 | 输出 |
|------|------|
| 各项目周报 | 部门看板卡片 |
| Wiki/妙记/群文档 | Top3 精选列表 |

## Top3 评分规则

1. **类型权重（高）**：SOP / 教程 / 培训 / 复盘 → 高分
2. **时效（中）**：本周新增/修改 → 高
3. **跨项目价值（中）**：多项目可复用 → 高
4. **完整度（低）**：200 字+、结构清晰 → 高

## 依赖

- `shared/skills/lark-api`
- `shared/skills/data-collection`
- `shared/skills/prompt-template`
- `shared/skills/card-builder`
- `shared/skills/llm-wiki-builder`
