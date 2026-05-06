---
name: project-bulletin-workflow
description: Handle Project bulletin / Weekly bulletin style dashboard-production workflows driven by user-provided markdown files. Use this whenever the user asks to根据md生成周报、项目简报、飞书卡片、对应前端页面, or mentions paths under J:\\Desktop\\code练习\\cursor_project\\dashboard_example\\Project bulletin or Weekly bulletin, especially when the workflow involves copying an existing frontend project into J:\\Desktop\\code练习\\cursor_project\\dashboard_example\\workspace, modifying the frontend content from the md, starting the frontend locally, and returning a Feishu card that links to localhost:3001-3006. Also use this when the user references projects like 01_垂类达人孵化, 06_虚拟IP孵化与运营, md_example templates, or asks to keep card output and local dashboard output in sync.
---

# Project Bulletin Workflow

## Purpose

This skill captures the user's preferred production workflow for bulletin-style dashboard projects.

The goal is not just to generate content, but to complete the whole delivery loop:
1. read the user's md input,
2. generate or send the Feishu card,
3. clone/copy the matching bulletin frontend project into the workspace area,
4. modify the frontend content to match the md,
5. start the frontend locally,
6. ensure the card can click through to a working localhost page.

## Known project locations

Treat these as preferred source projects when they exist:

- `J:\Desktop\code练习\cursor_project\dashboard_example\Project bulletin\06_虚拟IP孵化与运营`
- `J:\Desktop\code练习\cursor_project\dashboard_example\Project bulletin\01_垂类达人孵化`
- other sibling projects under `J:\Desktop\code练习\cursor_project\dashboard_example\Project bulletin`
- md templates under `J:\Desktop\code练习\cursor_project\dashboard_example\Project bulletin\md_example`
- workspace target root: `J:\Desktop\code练习\cursor_project\dashboard_example\workspace`

For weekly bulletin style work, also prefer the user's remembered reference mother template when relevant.

## Default workflow

Follow this sequence unless the user explicitly asks for a subset only.

### Step 1: Identify the source project and expected output

Determine:
- which bulletin frontend project should be used as the source,
- whether the user wants just a card, just a frontend page, or both,
- whether the md is a template, filled business data, or only partial notes,
- which localhost port should be used.

If the user does not specify a port, prefer a free one from:
- `3001`
- `3002`
- `3003`
- `3004`
- `3005`
- `3006`

### Step 2: Read and normalize the md

Extract the following whenever possible:
- title / period / subtitle
- hero KPIs
- platform or module sections
- tasks / risks / AI suggestions
- card summary sentence
- desired destination URL for the card button

If the md is incomplete, infer only lightweight presentation structure. Do not fabricate critical business facts unless the user clearly wants a demo.

### Step 3: Produce the Feishu card

Generate a card that matches the md and the intended use case:
- management brief,
- dashboard entry card,
- weekly/project summary,
- summary card with CTA button.

Prefer stable, client-compatible structures.
If a chart-heavy card might degrade in Feishu clients, prepare a compatible summary card fallback.

When the user wants actual sending, use the established Feishu card sending workflow already remembered in long-term memory.

### Step 4: Copy the frontend project into workspace

Copy the chosen source project into:
- `J:\Desktop\code练习\cursor_project\dashboard_example\workspace\<project-name-or-task-name>`

Guidelines:
- preserve the source project,
- modify the copied version only,
- keep naming clear and traceable,
- if re-running for the same project, either overwrite intentionally or create a versioned folder depending on the user's intent.

### Step 5: Modify the frontend content

Update the copied project so that it matches the md.

Prefer changing:
- data files,
- demo/mock data sources,
- page copy,
- module titles,
- chart data,
- task/risk/advice sections,
- CTA link targets.

Preserve the original visual system, layout logic, and component structure unless the user asks for structural redesign.

### Step 6: Start the frontend locally

Run the local frontend in the copied workspace project.

Requirements:
- ensure dependencies are available,
- use a valid port in `3001-3006`,
- confirm the dev server actually started,
- use the resulting localhost URL in the card CTA.

If a requested port is occupied, move to another allowed port and reflect that in the final card/link.

### Step 7: Final delivery

Return to the user with:
- the card result or send status,
- the copied frontend path,
- the localhost address,
- any caveats such as compatibility fallback or missing md fields.

## Output expectations

When the user provides an md for this workflow, the default expectation is:

1. produce the card,
2. copy and modify the related frontend project,
3. start the frontend,
4. make sure the card links to a working localhost page.

Do not stop at only writing a template unless the user specifically asked only for a template.

## Guardrails

- Prefer editing copied projects, not the original source project.
- Keep card content and frontend content consistent.
- If the md is only a draft, tell the user what was inferred.
- If localhost startup fails, report the failure clearly and do not pretend it works.
- If a port changes, update the card link accordingly.

## Typical trigger examples

- “根据这个 md 给我发卡片，并把 Project bulletin 前端跑起来”
- “参考 06_虚拟IP孵化与运营，把前端复制到 workspace 并改内容”
- “后续给你 md，你就按这个工作流直接出卡片和 localhost 页面”
- “用 01_垂类达人孵化 那套项目，改成新的周报并启动到 3003”
