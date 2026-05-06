---
name: openclaw-frontend-gateway
description: Build or review a custom frontend integration for OpenClaw using the preferred architecture: browser frontend -> your own backend -> local/private OpenClaw Gateway HTTP API (/v1/chat/completions). Use when the user asks how to connect a web app, React/Vue/Vite frontend, custom UI, or local chat panel to OpenClaw, especially when token safety and backend proxying matter.
---

# OpenClaw Frontend Gateway

Use this skill when the task is about wiring a custom frontend to OpenClaw.

## Default architecture

Always prefer this path unless the user explicitly asks for something else:

1. Browser frontend
2. Your own backend
3. Local/private OpenClaw Gateway
4. `POST /v1/chat/completions`

In shorthand:

`frontend -> backend -> OpenClaw Gateway -> agent`

## Core rule

Do **not** put the Gateway token in browser code.

Preferred pattern:
- frontend calls your own `/api/*`
- backend reads/holds the Gateway token
- backend forwards requests to OpenClaw Gateway

## What to check first

Before changing app code, verify:

1. Gateway is running
   - `openclaw gateway status`
   - usually on `127.0.0.1:18789`
2. HTTP endpoint is enabled
   - `gateway.http.endpoints.chatCompletions.enabled`
3. Auth exists
   - usually `gateway.auth.token`
4. Target agent is known
   - commonly `main`

On this machine, config usually lives at:
- `~/.openclaw/openclaw.json`

## Recommended request shape

Send an OpenAI-compatible HTTP request to:

```http
POST http://127.0.0.1:18789/v1/chat/completions
Authorization: Bearer <gateway-token>
x-openclaw-agent-id: main
Content-Type: application/json
```

Example body:

```json
{
  "model": "openclaw",
  "messages": [
    { "role": "user", "content": "你好" }
  ],
  "user": "custom-frontend"
}
```

## Backend pattern

Use a backend proxy layer.

Typical responsibilities:
- expose `/api/chat`
- validate/sanitize frontend input
- read Gateway config from env or `~/.openclaw/openclaw.json`
- attach `Authorization: Bearer ...`
- attach `x-openclaw-agent-id`
- forward to `/v1/chat/completions`
- return simplified JSON to the frontend

Preferred config order:
1. explicit env vars
2. `~/.openclaw/openclaw.json`
3. safe defaults

Useful env names:
- `OPENCLAW_GATEWAY_URL`
- `OPENCLAW_GATEWAY_PORT`
- `OPENCLAW_GATEWAY_TOKEN`
- `OPENCLAW_AGENT_ID`
- `OPENCLAW_CONFIG_PATH`

## Frontend pattern

Frontend should:
- call your own backend, not Gateway directly
- avoid storing tokens
- display request / loading / error / response states cleanly
- optionally support streaming later

Common local dev setup:
- frontend dev server on `5173`
- backend on `3001`
- Vite proxy `/api` -> `http://127.0.0.1:3001`

## Preferred defaults for Lu

When Lu asks about custom frontend integration, assume this preferred architecture:
- local or private Gateway
- token kept on backend only
- frontend talks to backend `/api/*`
- backend forwards to OpenClaw `/v1/chat/completions`

If asked to "directly connect" a frontend, still prefer a backend proxy unless Lu explicitly accepts exposing credentials in a trusted environment.

## Good implementation steps

1. inspect the frontend project structure
2. inspect whether a backend already exists
3. verify Gateway health with `openclaw gateway status`
4. wire or update backend proxy to `/v1/chat/completions`
5. keep token/config out of frontend source
6. add a health endpoint like `/api/health`
7. test one real request end-to-end
8. only then refine UX (streaming, history, agent switch, markdown)

## When answering

Optimize for practical guidance:
- show the architecture clearly
- explain why backend proxying is preferred
- point out exact headers/body fields needed
- if codebase access is available, modify the project directly
- if the current code hardcodes the token, replace that with config/env loading

## Avoid

Avoid recommending:
- putting Gateway token in frontend JS/TS
- browser direct calls to a private local Gateway with exposed secrets
- overcomplicated infra when a local backend proxy is enough
- describing the integration as CLI-only if HTTP Gateway is already available
