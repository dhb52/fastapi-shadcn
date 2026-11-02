---
name: fastapi-shadcn
description: >-
  Build FastAPI + React/shadcn web apps: scaffold a modular async backend and Vite frontend,
  add slowapi rate limits, captcha, Alembic migrations with selectable revision IDs,
  SQLite/PostgreSQL switching, optional Celery, Docker, and pre-commit hooks.
  Use when building or extending a FastAPI + shadcn/ui project, choosing a project
  template, or adding auth-adjacent security features.
---

# FastAPI + shadcn Web App

Default stack: Python 3.12 + uv + FastAPI + async SQLAlchemy + Alembic + slowapi + captcha; React 19 + Vite + Tailwind v4 + shadcn/ui + i18next + Biome; one root pre-commit config.

The canonical code is `assets/scaffold/`. Read `references/` for extension recipes. Do not create a second boilerplate pattern beside the scaffold.

## Choose the path

- **New project**: run `scripts/scaffold.sh <target> [--rev-id-style sequential|random]`. It copies the scaffold, installs dependencies, creates the first migration, and installs Git hooks.
- **Existing project**: keep its structure. Apply only the recipes that match the request: `references/backend.md`, `references/frontend.md`, `references/engineering.md`.
- **Template question**: read `references/layout.md` before recommending a different project generator.

## Workflow

### 1. Lock the stack decisions

Confirm only what changes the generated code:

- Database: SQLite for development, PostgreSQL for deployment.
- Alembic revision style: `sequential` (6-digit) or `random` (12 hex chars).
- Celery: needed or not.
- assistant-ui: needed or not.

Do not ask about values already fixed below.

### 2. Scaffold or inspect

For a new project:

```bash
./scripts/scaffold.sh ../my-app --rev-id-style sequential
```

Completion: `backend/uv.lock`, `frontend` lockfile, and `backend/alembic/versions/000001_initial_schema.py` exist.

For an existing project, inspect `pyproject.toml`, `package.json`, `alembic.ini`, and the current Git hooks before editing. Completion: you know which recipe applies and have not duplicated an existing pattern.

### 3. Backend

Work in `backend/`. Use uv for every Python command.

- Add a feature as `app/modules/<feature>/` with `router.py`, `schemas.py`, `models.py`, and `service.py`. Register its router in `app/api/v1/router.py` and its model in `app/db/registry.py`.
- Keep request handlers on `AsyncSession` from `app/api/deps.py`.
- Generate migrations with `uv run alembic revision --autogenerate -m "..."`, then inspect the file before `uv run alembic upgrade head`.
- Apply slowapi to write/auth routes with the router decorator above `@limiter.limit(...)`. Keep `request: Request` and `response: Response` parameters.
- Captcha is disabled by default. Test it with `CAPTCHA_ENABLED=true`. The frontend reads `/api/v1/config` and hides the field when false.
- Celery lives in `app/worker.py` and is installed with `uv sync --extra worker`.

Completion: `uv run alembic upgrade head`, `uv run pytest -q`, `uv run ruff check app`, and `uv run mypy app` all pass; `uv run fastapi dev` serves `/api/v1/health`.

### 4. Frontend

Work in `frontend/`. Detect the package manager:

1. `bun.lock` or `bun.lockb` -> `bun`
2. `pnpm-lock.yaml` -> `pnpm`
3. `package-lock.json` -> `npm`

Install with the detected manager, then run its script form (`bun run build`, `pnpm build`, `npm run build`). Use `bunx --bun shadcn@latest add <component>` for new shadcn components; use `pnpm dlx` or `npx` only when bun is absent.

Keep server state in `src/features/<feature>/`; keep shadcn primitives in `src/components/ui/`. API calls go through `src/lib/api.ts`. Keep user-visible strings in `src/i18n/locales/` and render them with `useTranslation`; add a locale by extending `src/i18n/index.ts`. The Vite dev proxy sends `/api` to `http://127.0.0.1:8000`; `VITE_API_URL` overrides it for split deployments.

Completion: typecheck, lint (`biome check`), and production build pass; the captcha field appears only when the backend reports it enabled.

### 5. Engineering

The root `.pre-commit-config.yaml` owns both subprojects. Install with `uv run --directory backend pre-commit install`; run `uv run --directory backend pre-commit run --all-files`.

Hooks: ruff check/format, mypy, Biome, TypeScript. All run locally, so no hook fetches from the network. Do not add Husky; it changes `core.hooksPath` and bypasses pre-commit.

Completion: all hooks pass on a clean tree.

### 6. Docker

Build `backend/` with `docker build -t my-api backend`. The image uses `fastapi run` and does not run migrations at startup. Run `alembic upgrade head` as a separate release step.

Completion: container returns `{"status":"ok"}` from `/api/v1/health`.

## Backend recipes

Read `references/backend.md` for:

- new feature module checklist
- async session and transaction rules
- Alembic `sequential`/`random` behavior and SQLite batch mode
- PostgreSQL switch
- slowapi storage and proxy notes
- captcha token design and how to call `verify_captcha_or_raise`
- Celery worker and Docker build args

## Frontend recipes

Read `references/frontend.md` for:

- package-manager command matrix
- shadcn component additions and `components.json`
- API client, config hook, and captcha field behavior
- Biome rules and generated-component exclusions

## Optional assistant-ui

Read `references/assistant-ui.md`. Use it only when the user asks for AI chat. The base scaffold has no LLM endpoint; wire `useLocalRuntime` to the app's real streaming route. Do not ship a fake echo backend.

## Hard rules

- Use `uv run` for backend commands; never bare `python`/`pip`.
- Use the signed HMAC captcha token. The token payload must contain only the digest, never the answer.
- Keep captcha disabled in development unless explicitly testing the captcha path.
- Apply slowapi limits per route; captcha issuance is `10/minute`, verification is `20/minute`.
- Keep migration execution out of application startup.
- Keep `backend/.gitignore` and `frontend/.gitignore` independent.
- Keep generated shadcn primitives in `src/components/ui/`; put app code in `src/features/`.
