# File Contract

## Root folder

Each task lives under:

```text
<main-workspace>/swarm-jobs/<job-id>/
```

## Required files

- `request.md`: original user task, normalized by `research-bot-manager`
- `plan.md`: dictator output
- `results/`: td output folder
- `report.md`: writer narrative output
- `paper/`: writer paper output folder
- `paper/main.tex`: required LaTeX manuscript entrypoint
- `status.json`: machine-readable stage status

## Naming rules

Use these exact filenames unless the user explicitly asks for a different contract.

## `status.json` shape

```json
{
  "jobId": "20260328-143500-short-title",
  "title": "short-title",
  "stage": "planned",
  "owner": "research-bot-dictator",
  "state": "in_progress",
  "updatedAt": "2026-03-28T06:35:00Z",
  "notes": []
}
```

## Allowed stage values

- `created`
- `planned`
- `executing`
- `reporting`
- `done`
- `blocked`

## Allowed state values

- `pending`
- `in_progress`
- `done`
- `failed`

## Results folder contents

Allow any structure under `results/`, but prefer:
- `results/code/`
- `results/docs/`
- `results/logs/`
- `results/data/`
- `results/assets/`

## Paper output contract

Writer must additionally create a paper folder:

```text
paper/
  main.tex
  sections/
  references.bib
```

Minimum acceptable paper output:
- `paper/main.tex` exists
- manuscript is based on actual artifacts, not guesses
- if evidence is incomplete, the LaTeX draft must say so explicitly rather than fabricate a paper-ready claim
