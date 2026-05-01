# insight-llm

LLM 洞察生成能力，负责将数据分析结果转化为可读的文字洞察。

## 能力

- 将结构化数据转为自然语言描述
- 生成趋势解读和原因分析
- 提炼关键结论和行动建议
- 适配不同受众（部门负责人 vs 项目负责人 vs 团队成员）

## 输入

```json
{
  "data": { "分析结果" },
  "audience": "department_head | project_manager | team_member",
  "tone": "formal | casual",
  "length": "short | medium | long"
}
```

## 输出

Markdown 格式的洞察文本，包含：
1. 一句话总结
2. 关键发现（带数据支撑）
3. 趋势判断
4. 建议行动

## 使用方式

通过 LLM API 调用，使用 prompts/ 下的 insight-*.md 模板。
