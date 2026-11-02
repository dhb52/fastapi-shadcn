# FastAPI + shadcn Web App

Modular FastAPI backend with async SQLAlchemy, Alembic, slowapi, captcha, and an optional Celery worker. React + Vite + shadcn/ui frontend.

## Requirements

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Bun, pnpm, or npm (bun preferred)
- Docker (optional, for PostgreSQL/Redis and the backend image)

## Backend

```bash
cd backend
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run fastapi dev
```

API docs: `http://127.0.0.1:8000/docs`

Create a migration:

```bash
uv run alembic revision --autogenerate -m "add something"
uv run alembic upgrade head
```

The revision ID style is configured in `alembic.ini`:

```ini
rev_id_style = sequential   ; 6-digit IDs, or random (12 hex chars)
```

Sequential IDs do not control migration order; `down_revision` does.

Enable the captcha path locally:

```bash
CAPTCHA_ENABLED=true uv run fastapi dev
```

The frontend reads `/api/v1/config` and only renders the captcha field when the backend reports it enabled.

## Frontend

```bash
cd frontend
bun install
bun run dev
```

With pnpm or npm:

```bash
pnpm install && pnpm dev
npm install && npm run dev
```

Add another shadcn component:

```bash
bunx --bun shadcn@latest add dialog
```

## PostgreSQL and Redis

```bash
docker compose up -d db redis
```

Set in `backend/.env`:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app
RATE_LIMIT_STORAGE_URI=redis://localhost:6379/1
```

Then run `uv run alembic upgrade head` again.

## Celery (optional)

```bash
cd backend
uv sync --extra worker
uv run celery -A app.worker.celery_app worker -l info
```

## Pre-commit

```bash
git add -A
uv run --directory backend pre-commit install
uv run --directory backend pre-commit run --all-files
```

The root config runs local ruff, mypy, Biome, and TypeScript hooks on both subprojects; no hook fetches from the network. Frontend hooks use `node_modules/.bin`, so they work with any package manager after install.

## Docker

```bash
docker build -t fastapi-shadcn-backend backend
docker run --rm -p 8000:8000 fastapi-shadcn-backend
```

The image defaults to SQLite at `/data/app.db` and owns `/data` as `nonroot`. For PostgreSQL, pass the URL explicitly:

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:password@host:5432/app \
  fastapi-shadcn-backend
```

Migrations are a separate release step; do not run `alembic upgrade head` from application startup when running multiple replicas.
