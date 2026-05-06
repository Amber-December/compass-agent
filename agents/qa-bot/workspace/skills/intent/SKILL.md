---
name: intent
description: "意图识别 — 分析用户输入，判断意图类别并路由到对应 Skill"
metadata:
  {
    "openclaw":
      {
        "emoji": "🎯",
      },
  }
---

# intent Skill

> 意图识别 — 分析用户输入，判断意图类别并路由到对应 Skill

## 归属

- **Agent**: qa-bot
- **路径**: `agents/qa-bot/workspace/skills/intent/`

## 触发条件

- 所有用户输入都需要经过意图识别
- 作为 qa-bot 的入口 Skill

## 核心能力

### 1. 意图分类

| 意图类别 | 触发关键词 | 处理方式 | 目标 Skill |
|----------|-----------|----------|-----------|
| **知识查询** | "什么是..." "如何..." "为什么..." "介绍下..." | 检索 workspace/knowledge/wiki/ 生成回答 | query |
| **数据查询** | "看数据" "分析效能" "KPI 多少" "本周数据" | 读取 workspace/knowledge/data/ 生成回答 | data-query |
| **图谱查询** | "知识图谱" "关系图" "关联分析" "看看图谱" | 打开/描述 workspace/knowledge/graph/ | graph-query |
| **刷新知识库** | "刷新知识库" "同步知识库" "/wiki-sync" "ingest" | 调用 wiki-manager | route |
| **生成周报** | "生成周报" "部门看板" "周报汇总" | 调用 weekly-reporter | route |
| **推送卡片** | "发通知" "推送卡片" "发消息" | 调用 card-builder | route |
| **个人介绍** | "你是谁" "你能做什么" "介绍一下自己" | 返回个人介绍 | query |
| **闲聊/其他** | 纯问候、与业务无关的闲聊 | 礼貌回应并引导 | query |

### 2. 意图识别逻辑

```python
def recognize_intent(question: str) -> str:
    """识别用户意图"""
    question_lower = question.lower()
    
    # 操作类意图（高优先级）
    if any(kw in question_lower for kw in ["刷新", "同步", "wiki-sync", "ingest"]):
        return "refresh_knowledge"
    
    if any(kw in question_lower for kw in ["周报", "看板", "汇总"]):
        return "generate_weekly"
    
    if any(kw in question_lower for kw in ["通知", "推送", "发消息"]):
        return "push_card"
    
    # 查询类意图
    if any(kw in question_lower for kw in ["图谱", "关系图", "关联", "网络"]):
        return "graph_query"
    
    if any(kw in question_lower for kw in ["数据", "kpi", "效能", "转化率", "gmv"]):
        return "data_query"
    
    if any(kw in question_lower for kw in ["是什么", "如何", "为什么", "介绍", "sop"]):
        return "knowledge_query"
    
    # 个人介绍
    if any(kw in question_lower for kw in ["你是谁", "你能做什么", "介绍自己"]):
        return "personal_intro"
    
    # 默认：知识查询
    return "knowledge_query"
```

## 意图路由

```python
def route_intent(intent: str, question: str, scope: str | None = None):
    """根据意图路由到对应 Skill"""
    
    if intent == "knowledge_query":
        # 调用 query skill
        return query_skill.answer(question, scope)
    
    elif intent == "data_query":
        # 调用 data-query skill
        return data_query_skill.answer(question, scope)
    
    elif intent == "graph_query":
        # 调用 graph-query skill
        return graph_query_skill.answer(question, scope)
    
    elif intent == "refresh_knowledge":
        # 调用 route skill，触发 wiki-manager
        return route_skill.dispatch("wiki-manager", "sync")
    
    elif intent == "generate_weekly":
        # 调用 route skill，触发 weekly-reporter
        return route_skill.dispatch("weekly-reporter", "generate")
    
    elif intent == "push_card":
        # 调用 route skill，触发 card-builder
        return route_skill.dispatch("card-builder", "push")
    
    elif intent == "personal_intro":
        # 返回个人介绍
        return query_skill.personal_intro()
    
    else:
        # 默认：知识查询
        return query_skill.answer(question, scope)
```

## 输出格式

**意图识别结果**（只输出 JSON，不输出任何分析文字）：
```json
{
  "intent": "knowledge_query",
  "confidence": 0.95,
  "target_skill": "query",
  "scope": "kol-incubation"
}
```

## 红线

- **只输出一条消息** — 意图识别结果必须是单一 JSON，不拆多条
- **意图识别必须快速**，避免阻塞用户
- **严禁输出思考过程** — 只返回 JSON 结果，严禁输出"我分析一下"、"这个看起来像是"等分析文字
- **置信度低于 0.7 时**，默认走知识查询
- **操作类意图必须确认**，避免误触发
- **闲聊意图要礼貌引导**回工作话题
