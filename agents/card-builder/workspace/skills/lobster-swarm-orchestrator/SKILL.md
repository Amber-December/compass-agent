---
name: lobster-swarm-orchestrator
description: Coordinate a multi-agent OpenClaw research swarm where main handles user intake and research-bot-manager acts as the swarm coordinator over research-bot-dictator, research-bot-td, and research-bot-writer. Use when a request needs staged research planning, experiment execution, folder-based artifacts, fixed file names, or handoffs between specialized lobsters.
---

# Lobster Swarm Orchestrator

Use this skill when the main lobster must decide whether to answer directly or hand work to the manager-led lobster pipeline.

## Decision rule

Answer directly when the task is simple, low-risk, and does not need staged research or artifact production.

Delegate when any of these are true:
- The request needs research planning before execution.
- The task needs implementation, experiments, or multi-step validation.
- The user wants files, folders, reports, or durable outputs.
- The task is large enough that one turn would be messy or fragile.

## Standard swarm roles

- `main`: user-facing intake, triage, and final user update.
- `research-bot-manager`: swarm coordinator; creates the job folder, delegates stages, gates handoffs, checks artifacts, and reports status back to main.
- `research-bot-dictator`: convert the request into an execution plan.
- `research-bot-td`: execute the plan, run experiments, and place outputs in the project folder.
- `research-bot-writer`: read the full project folder and write the final report.

## Required project layout

Create a job folder before delegation. Use the bundled scripts:
- `scripts/new_job.ps1 -Title "<short title>"`
- `scripts/run_swarm_job.ps1 -Title "<short title>" -RequestText "<normalized request>"`

The script creates:
- `swarm-jobs/<job-id>/request.md`
- `swarm-jobs/<job-id>/plan.md`
- `swarm-jobs/<job-id>/results/`
- `swarm-jobs/<job-id>/report.md`
- `swarm-jobs/<job-id>/status.json`

Use these fixed filenames unless the user explicitly asks otherwise.

## Handoff contract

### 1) main -> research-bot-manager

Give manager:
- the user goal
- constraints
- success criteria
- any path/output requirements
- an instruction to coordinate the full swarm

### 2) research-bot-manager -> dictator

Manager gives dictator:
- the normalized request
- the job folder path
- an instruction to write only `plan.md`

### 3) research-bot-manager -> td

After `plan.md` is substantively complete, manager allows TD to proceed.

TD reads:
- `request.md`
- `plan.md`

TD must place all execution artifacts under `results/` and update `status.json`.

### 4) research-bot-manager -> writer

After `results/` contains substantive artifacts, manager allows writer to proceed.

Writer reads the entire job folder, especially:
- `request.md`
- `plan.md`
- `results/`
- `status.json`

Writer writes the polished final report to `report.md` and `paper/main.tex`.

## Delegation mechanism

When operating from the main lobster, hand orchestration to `research-bot-manager` rather than directly supervising dictator / td / writer.

Manager may then invoke the dedicated agents explicitly with the OpenClaw CLI so the right workspace/persona is used:

```powershell
openclaw agent --agent research-bot-dictator --message "<instruction>"
openclaw agent --agent research-bot-td --message "<instruction>"
openclaw agent --agent research-bot-writer --message "<instruction>"
```

Do not deliver those internal handoff messages to user chat.

## Manager behavior

- `research-bot-manager` owns swarm supervision.
- Keep the user updated at stage boundaries, not every tiny step.
- If a delegated stage fails, summarize the blocker and either retry with a narrower instruction or ask the user.
- Always point the next lobster at the same job folder.
- Main should read `report.md` before replying to the user with a final answer; otherwise summarize the current state honestly.

## Output quality gates

Do not treat the swarm as complete until:
- `plan.md` exists
- `results/` contains actual artifacts or a clear failure record
- `report.md` exists for report-style tasks

## References

Read `references/workflow.md` for the full stage checklist and message templates.
Read `references/file-contract.md` for fixed filenames and artifact rules.
