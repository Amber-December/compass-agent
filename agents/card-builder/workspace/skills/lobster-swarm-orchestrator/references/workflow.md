# Swarm Workflow

## 1. Intake

Main agent decides:
- direct answer
- or swarm execution

For swarm execution, hand orchestration to `research-bot-manager`.
The manager is responsible for creating the job folder and supervising dictator -> td -> writer.

## 2. Manager creates job folder

`research-bot-manager` creates the job folder.

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\lobster-swarm-orchestrator\scripts\new_job.ps1 -Title "short-title"
```

Then manager writes the normalized user request into `request.md`.

## 3. Dictator stage

`research-bot-manager` sends dictator a strict instruction:
- read the request
- write a concrete plan to `plan.md`
- include scope, assumptions, steps, risks, deliverables, and stop conditions
- do not start implementation

Suggested message template:

```text
You are the planning lobster.
Job folder: <absolute-path>
Read request.md.
Write an execution plan to plan.md only.
Do not implement the plan.
Include: objective, assumptions, task breakdown, validation plan, risks, and expected outputs.
```

## 4. TD stage

After validating that `plan.md` is substantive, `research-bot-manager` sends TD a strict instruction:
- read `request.md` and `plan.md`
- execute the plan
- put all code, notes, logs, and outputs under `results/`
- update `status.json`

Suggested message template:

```text
You are the execution lobster.
Job folder: <absolute-path>
Read request.md and plan.md.
Execute the plan.
Put all artifacts under results/.
Update status.json with progress, outcome, and notable issues.
```

## 5. Writer stage

After validating that `results/` contains substantive artifacts, `research-bot-manager` sends writer a strict instruction:
- read the full folder
- write `report.md`
- also create `paper/main.tex`
- report and paper draft should reflect what actually happened, not just the plan

Suggested message template:

```text
You are the reporting lobster.
Job folder: <absolute-path>
Read request.md, plan.md, results/, and status.json.
Write a polished report to report.md.
Also create a paper draft at paper/main.tex.
Cover: objective, approach, what was done, outputs, limitations, next steps, and explicit evidence boundaries.
```

## 6. Final response

`research-bot-manager` verifies that required artifacts exist and reports status back to main.

Main agent reads `report.md` and sends the user:
- a concise summary
- the job folder path
- unresolved risks if any
