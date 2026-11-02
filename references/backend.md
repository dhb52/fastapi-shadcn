# Backend

## Add a feature module

Create `app/modules/<feature>/`:

```text
__init__.py
models.py      SQLAlchemy models, import Base from app.db.base
schemas.py     Pydantic request/response models
service.py     business logic, receives AsyncSession
router.py      HTTP layer, uses SessionDep
```

Then:

1. Import the model module in `app/db/registry.py`.
2. Include the router in `app/api/v1/router.py`.
3. Generate a migration: `uv run alembic revision --autogenerate -m "add <feature>"`.
4. Inspect the generated file, then run `uv run alembic upgrade head`.

Use `Note` in `app/modules/notes/` as the reference: model, `ConfigDict(from_attributes=True)` read schema, service methods, `SessionDep` router, and explicit `NoteRead.model_validate(...)` at the HTTP boundary.

## Database session

- `app/db/session.py` owns the engine and `async_sessionmaker(expire_on_commit=False)`.
- Handlers depend on `SessionDep`; never create an engine or session inside a handler.
- Services commit their own transaction with `await session.commit()`. After commit, `await session.refresh(obj)` when the response needs generated columns.
- `app/main.py` disposes the engine in the FastAPI lifespan.
- SQLite and PostgreSQL share the same async code path. Only `DATABASE_URL` changes:
  - `sqlite+aiosqlite:///./app.db`
  - `postgresql+asyncpg://user:password@host:5432/db`
- Bare `postgres://` and `postgresql://` URLs are normalized to `postgresql+asyncpg://` in `app/core/config.py`.

## Alembic

`alembic.ini` controls the revision ID style:

```ini
rev_id_style = sequential
file_template = %%(rev)s_%%(slug)s
revision_environment = true
```

`app/core/rev_id.py` implements:

- `sequential`: finds the largest 6-digit numeric revision and writes the next zero-padded value. `000001`, `000002`, ...; raises after `999999`.
- `random`: `secrets.token_hex(6)`, 12 lowercase hex characters.
- Explicit `alembic revision --rev-id custom123` wins; the hook returns early when the CLI supplied an ID.

Sequential IDs are for readability. Alembic orders migrations by `down_revision`; renaming or inserting a numeric ID does not change history. For random IDs the scaffold uses a date-prefixed `file_template` so filenames sort approximately by creation time.

SQLite uses `render_as_batch=True` because SQLite cannot alter columns in place. PostgreSQL uses normal DDL. `compare_type=True` catches column type drift.

Offline mode uses the same target metadata. Online mode builds an async engine from the config section after `config.set_main_option("sqlalchemy.url", ...)`.

## Rate limiting

`app/core/limiter.py` creates one `Limiter` with `get_remote_address`, `headers_enabled=True`, and storage from `RATE_LIMIT_STORAGE_URI`.

Decorator order matters:

```python
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, response: Response, ...):
    ...
```

- The route decorator must be above `@limiter.limit`.
- Keep `request: Request`; slowapi needs it.
- Keep `response: Response` when `headers_enabled=True`.
- Default storage is `memory://`; use `redis://...` for multi-worker deployments. `redis` is a base dependency.
- `get_remote_address` reads `request.client.host`. Behind a trusted proxy, configure Uvicorn/FastAPI CLI with `--proxy-headers`; do not parse `X-Forwarded-For` manually.

Captcha limits: issuance `10/minute`, verification `20/minute`.

## Captcha

`app/modules/auth/captcha.py`:

- Generates a 5-character code from `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` with `secrets.choice`.
- Renders a PNG with `captcha.image.ImageCaptcha` and returns a `data:image/png;base64,...` URL.
- Signs a token with `itsdangerous.URLSafeTimedSerializer`.
- The token payload is `{"d": "<HMAC-SHA256 of normalized answer>"}`. The answer is never in the token.
- `verify_captcha_token` checks signature, TTL, and `hmac.compare_digest` on the digest.
- `verify_captcha_or_raise` returns immediately when `CAPTCHA_ENABLED` is false, otherwise raises 400 on failure.

`app/modules/auth/router.py` exposes `GET /auth/captcha` and `POST /auth/captcha/verify`. When disabled, both return 404.

Wire the dependency into a real login/registration handler:

```python
from app.modules.auth.captcha import verify_captcha_or_raise

verify_captcha_or_raise(payload.captcha_token, payload.captcha_code)
# then verify credentials
```

The UI reads `captcha_enabled` from `GET /api/v1/config`. Development default is false; production sets `CAPTCHA_ENABLED=true`.

Stateless tokens are replayable within the TTL by design. Keep the TTL short (300 seconds) and rate-limit issuance. For one-time use, add a Redis `jti` consumed on verification; keep the answer out of the token either way.

## Celery

`app/worker.py` defines `celery_app` and a `ping` task. It uses `REDIS_URL` as broker and backend.

```bash
uv sync --extra worker
uv run celery -A app.worker.celery_app worker -l info
```

The web image does not install the worker extra by default. Build a worker image with:

```bash
docker build --build-arg UV_EXTRAS="--extra worker" -t my-api-worker backend
```

Import `app.worker` only from worker processes; do not import it in the FastAPI app.

## Docker

The Dockerfile uses `python:3.12-slim-bookworm` and copies `uv` from `ghcr.io/astral-sh/uv:0.9.26`.

- Build context: `backend/`.
- `uv sync --frozen --no-dev` installs from `uv.lock`.
- The runtime image copies `/app` from the builder, puts `.venv/bin` on `PATH`, and runs as `nonroot`.
- `/data` is owned by `nonroot` and used for the default SQLite URL (`sqlite+aiosqlite:////data/app.db`), so the container works without a writable `/app`.
- `CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]`.
- Run `alembic upgrade head` as a separate release/job step. Do not add it to application startup when multiple replicas may start at once.

`.dockerignore` excludes `.venv`, caches, tests, `*.db`, and `.env`.

## Verification

```bash
uv run ruff check app tests alembic
uv run ruff format --check app tests alembic
uv run mypy app
uv run pytest -q
uv run alembic upgrade head
uv run fastapi dev
```
