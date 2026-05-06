---
name: feishu-card-builder-send
description: Create, edit, and prepare Feishu cards for delivery. Use whenever the user asks to 写飞书卡片, 编辑飞书卡片, 生成卡片 JSON, 发送飞书卡片, build a Feishu/Lark card, convert content into a Feishu interactive card, or design a card that opens a web dashboard. This skill covers card JSON v2 authoring, choosing between static display vs lightweight interaction, mapping business content into card components, and explaining the correct send path through app bots or custom bots.
---

# Feishu Card Builder + Send

Turn business content into a practical Feishu card that is ready to send through the correct Feishu channel.

## What this skill does

Use this skill to:
- draft a Feishu card from raw text, markdown, dashboard requirements, alerts, KPIs, or workflow actions
- edit an existing card JSON
- convert a dashboard summary into a card with a button that opens a web page
- decide whether the card should be static, interactive, or template-based
- explain how the card should be sent after it is authored

## Core model

Think in three layers:
1. **Card goal**: what the user needs the recipient to understand or do
2. **Card structure**: header, summary, KPI blocks, chart/table snippets, buttons, form actions
3. **Send path**: custom bot, app bot, card template, or interactive callback flow

Do not jump straight into JSON before deciding these three things.

## First decision: what kind of card is this?

Classify the request into one of these buckets:

### 1) Static notification card
Use when the card mainly informs.
Examples:
- business alerts
- KPI daily summary
- ranking / leaderboard
- release notice
- operation report

Typical ingredients:
- header/title
- short summary
- 1-4 KPI items
- optional table-like facts rendered as fields
- one button for “查看详情” / “打开看板”

### 2) Lightweight interactive card
Use when the user wants recipients to click, approve, vote, choose, or submit a simple form.
Examples:
- approval actions
- event signup
- poll / vote
- acknowledge / confirm

Typical ingredients:
- clear action area
- buttons / select menu / date picker / form elements
- callback note: interaction requires a Feishu app endpoint to receive actions

### 3) Dashboard entry card
Use when the card is a compact front door to a richer web dashboard.
Examples:
- monitoring center overview
- sales dashboard teaser
- project cockpit summary

Typical ingredients:
- concise KPIs only
- trend hint if useful
- strong CTA button that opens the dashboard URL

### 4) Reusable template card
Use when the same card shape will be sent repeatedly with different data.
Examples:
- daily report
- repeated campaign notice
- recurring alerts

Prefer template-oriented design and clearly mark variables that change.

## Working process

Follow this order.

### Step 1: normalize the input
Extract:
- audience: who receives it
- purpose: inform / prompt action / link out / collect input
- data source: static text, JSON, API response, dashboard summary, table, Feishu Bitable
- urgency: normal / warning / critical
- action target: no action, external URL, Feishu callback, dashboard jump

If details are missing, make the fewest reasonable assumptions and state them briefly.

### Step 2: choose the card shape
Before writing JSON, describe the chosen shape in 2-6 bullets:
- title
- sections
- main KPIs or facts
- action area
- whether it is static or interactive

### Step 3: write the card
Prefer Feishu card JSON v2 style.
Keep cards compact and scannable.

Good defaults:
- 1 clear title
- 1 short summary block
- 2-4 KPI facts max per row/section
- 1 primary button, optional secondary button
- avoid stacking too many dense sections in chat cards

### Step 4: provide the send path
Always tell the user which send path applies:
- **Custom bot**: simple message push into a group via webhook
- **App bot / app message API**: sending cards to users/groups with app credentials
- **Interactive bot flow**: required when card actions must trigger backend processing
- **Card template / CardKit**: useful when the same card is reused often

If the user asks to “send” but no bot/app context is provided, do not pretend the card is already deliverable. Say what is ready now and what credential/path is still needed.

## Feishu-specific design rules

Based on Feishu card usage patterns:
- cards are best for structured, compact, action-oriented communication
- use cards for chat messages, pinned content, and link previews
- use buttons to open a full web dashboard when detail is too large for chat
- use interactive components only when the workflow is simple and the backend can handle callbacks
- use reusable template thinking when repeated sends share one structure with changing variables

## Output modes

Choose one of these output modes depending on the request.

### Mode A: card proposal
Use when the user is still shaping the card.
Output:
- intent summary
- recommended card type
- content structure
- suggested send path

### Mode B: ready-to-edit JSON
Use when the user wants a concrete card.
Output exactly in this order:
1. short explanation
2. card JSON in a code block
3. brief send instructions

### Mode C: card revision
Use when the user gives existing JSON or asks for modifications.
Output:
- what changed
- revised JSON
- any compatibility or callback notes

### Mode D: card + dashboard handoff
Use when the card should open a frontend dashboard.
Output:
- concise card JSON
- expected target URL placeholder or real URL
- note that the card should stay summary-level while the page holds detail

## JSON authoring guidance

When writing card JSON:
- keep field names and structure consistent
- favor readability over showing every possible component
- use realistic placeholder values where business data is missing
- label placeholders clearly, e.g. `https://example.com/dashboard` or `${dashboard_url}`
- if interaction is used, mark callback-dependent parts explicitly

## Interaction rule

If the card contains submit / approve / vote / form actions, include a note like:

> This card requires a Feishu app backend to receive and process interaction callbacks; the JSON alone is not enough.

## Sending rule

If the user asks how to send the card, explain one of these routes:

### Route 1: custom bot webhook
Best for simple group notifications.
- author the card JSON
- send through a configured custom bot webhook
- good for static or mildly dynamic notifications

### Route 2: app bot / server-side API
Best for enterprise workflows.
- author the card JSON or template
- send via Feishu app credentials and message API
- supports broader enterprise delivery and updates

### Route 3: interactive workflow
Best for approvals/forms.
- author the card
- configure callback handling in the Feishu app backend
- process user actions and optionally update the card

### Route 4: CardKit/template-based reuse
Best for repeated campaigns/reports.
- create a reusable template
- fill variables at send time
- use template ID / card entity flow where appropriate

## When editing existing cards

If the user provides existing JSON:
1. identify whether it is structurally valid enough to preserve
2. keep unchanged sections when possible
3. improve clarity, hierarchy, and action placement
4. call out any likely incompatibilities or missing callback context

## For dashboard-oriented users

When the user is really asking for a dashboard but wants Feishu entry points:
- use the card as the summary and alert surface
- put only top KPIs, status, trend, and one or two actions in the card
- move dense charts and detailed tables into the linked web dashboard

## Template-style markdown → interactive chart card workflow

Use this workflow whenever the user gives you a structured `.md` document that behaves like a business template, weekly bulletin, KPI report, project report, or dashboard data sheet and wants a Feishu card back.

### Trigger conditions

Apply this flow when the input markdown contains sections like:
- basic info / 标题 / 周期
- KPI summary / Hero summary
- platform comparison
- daily trend data
- risks / tasks / AI advice
- explicit card instructions such as 飞书卡片 / 交互图表 / chart / 柱状图 / 折线图

### Default output shape

If the user gives a template-style markdown and asks for a card, prefer this structure:
1. title + period
2. 3-4 KPI blocks
3. one real `chart` component for bar comparison
4. one real `chart` component for line trend
5. short risk summary
6. optional CTA button

### Mapping guidance

Map markdown sections into card sections like this:
- 基本信息 → title / subtitle / period
- Hero Summary → KPI blocks
- platform comparison → bar chart
- 7-day trend data → line chart
- risks → markdown risk summary
- detail link → button or multi_url

### Chart authoring rule

When the user explicitly wants an interactive chart card, prefer real Feishu `chart` components instead of fake sparkline text.

Use patterns like:
- `tag: "chart"`
- `chart_spec.type: "bar"` for platform comparison
- `chart_spec.type: "line"` for trend analysis
- `seriesField` for legend-based switching
- `legends.visible: true`

### Reality check rule

Do not overclaim. A successful API send does not guarantee the recipient client rendered the chart interactively.
After send, distinguish clearly between:
- send success
- chart accepted by API
- chart actually rendered on recipient client

If the user says the client can render the chart, continue using real chart components for future markdown-to-card tasks.
If the client degrades, say so and offer a compatible fallback.

## Response template

When producing a concrete result, use this structure:

### 1. Card intent
- audience:
- purpose:
- card type:
- send path:

### 2. Card JSON
```json
{ }
```

### 3. Notes
- callback needed or not
- which values are placeholders
- where the detail page should live if there is a jump link

## Example trigger phrases
- “帮我写一个飞书卡片”
- “把这个通知做成飞书消息卡片”
- “给这个 dashboard 做个飞书入口卡片”
- “把这段 JSON 改成可交互卡片”
- “怎么发送飞书卡片”
- “做一个审批卡片”

## Important limits

Do not claim you have already sent a card unless the execution path and credentials are actually available.
Do not bury critical actions under too many decorative sections.
If the content is too large, recommend a card + web dashboard split instead of overstuffing the card.
