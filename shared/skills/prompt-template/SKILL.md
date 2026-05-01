# prompt-template

所有 Agent 共享的 Prompt 模板管理能力。

## 能力

- 按场景加载对应的 prompt 模板
- 变量替换（如 {{project_name}}, {{date_range}}）
- 模板版本管理

## 模板目录结构

```
prompts/
├── weekly-report.md      # 周报生成模板
├── dept-board.md         # 部门看板模板
├── risk-alert.md         # 风险预警模板
├── qa-answer.md          # Q&A 回答模板
├── top3-scoring.md       # Top3 精选评分模板
└── scenarios/
    └── mcn/              # MCN 场景专属模板
        ├── weekly-report.md
        └── risk-rules.md
```

## 使用方式

Agent 通过读取 `prompts/` 下的 Markdown 文件获取模板，使用双大括号 `{{variable}}` 进行变量替换。

## 模板规范

- 每个模板包含 **Role**、**Input**、**Output**、**Rules** 四个部分
- 输出格式优先使用 Markdown
- 模板顶部标注版本和适用场景
