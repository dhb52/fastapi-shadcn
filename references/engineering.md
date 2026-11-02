# Engineering

## Repository shape

```text
backend/            independent Python project, own .gitignore, uv.lock
frontend/           independent Node project, own .gitignore, lockfile
.pre-commit-config.yaml
compose.yaml        PostgreSQL + Redis for development
```

The root is one Git repository. `backend/` and `frontend/` are subprojects, not submodules. Each has its own `.gitignore`; the root one only covers OS/editor artifacts.

## Why one pre-commit config

Git has one hooks path per repository. Installing Husky changes `core.hooksPath` to `.husky/_` and disables the framework's hooks; installing pre-commit writes `.git/hooks/pre-commit`. Running both means one silently wins.

The scaffold installs pre-commit once at the root:

```bash
uv run --directory backend pre-commit install
uv run --directory backend pre-commit run --all-files
```

Hooks are scoped by `files:` and all run locally, so no hook needs a network fetch:

- `backend-ruff-check`: any backend Python file; full `app tests alembic` check with `--fix`
- `backend-ruff-format`: any backend Python file; full format pass
- `backend-mypy`: any backend Python file; full `app` check
- `frontend-biome`: staged frontend files, excluding generated `src/components/ui/`
- `frontend-typecheck`: any frontend change, full `tsc -p tsconfig.json --noEmit`

The full backend checks keep pre-commit independent of which files Git happened to stage. The tradeoff is a few seconds per commit; correctness beats a partial lint pass.

## Backend tooling

- uv owns the environment and lockfile.
- Ruff: lint + format, target `py312`, line length 100.
- mypy: strict app checks, Pydantic plugin, narrow third-party overrides for `captcha` and `celery`.
- pytest: async mode auto; in-memory SQLite with `StaticPool` for route tests.
- `pre-commit` is a dev dependency; `uv run --directory backend ...` works from the repository root.

## Frontend tooling

- Biome: format + lint in one pass.
- TypeScript: `tsc -p tsconfig.json --noEmit`.
- Vite build: `tsc -p tsconfig.json && vite build`.
- Hooks use `node_modules/.bin`, so no package-manager-specific invocation is baked into Git hooks.

## Commands

```bash
# backend
cd backend
uv sync
uv run fastapi dev
uv run pytest -q
uv run ruff check app tests alembic
uv run mypy app
uv run alembic revision --autogenerate -m "change"
uv run alembic upgrade head

# frontend
cd frontend
bun install
bun run dev
bun run typecheck
bun run lint
bun run build

# repository
uv run --directory backend pre-commit run --all-files
docker compose up -d db redis
docker build -t my-api backend
```

## Gitignore boundaries

`backend/.gitignore` covers `.venv`, Python caches, coverage, `*.db`, `.env` (keeps `.env.example`).

`frontend/.gitignore` covers `node_modules`, `dist`, `.vite`, coverage, `.env*` (keeps `.env.example`).

The root `.gitignore` covers `.DS_Store`, `.worktree/`, editor directories, and logs. Do not collapse the three files into one; the subprojects are portable on their own.
