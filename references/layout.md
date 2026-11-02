# Project layout

## Research summary (2026-11)

| Option | What it gives | Why it is not the base |
|---|---|---|
| `fastapi-fastio` 0.1.2 | `fastio create` CLI for service/monolith/monorepo, uv, Alembic, Celery, Docker | Alpha release; the declared homepage currently returns 404; generated layout is not shadcn-aware |
| `fastapi/full-stack-fastapi-template` | Maintained official full-stack template: React + Vite + shadcn, Docker Compose, pre-commit, Playwright | SQLModel + PostgreSQL only; no dev SQLite, slowapi, or captcha; larger auth/email/items surface |
| This scaffold | Feature modules, async SQLAlchemy, SQLite/PostgreSQL, slowapi, captcha, optional Celery, shadcn, one root pre-commit | Small by design; add auth and product features as modules |

Sources:

- https://pypi.org/project/fastapi-fastio/
- https://github.com/fastapi/full-stack-fastapi-template
- https://github.com/zhanymkanov/fastapi-best-practices
- https://fastapi.tiangolo.com/fastapi-cli/
- https://ui.shadcn.com/docs/installation/vite

## Chosen layout

```text
backend/
  app/
    main.py                  app factory + lifespan + middleware
    api/v1/router.py         composition root
    api/deps.py              shared dependencies
    core/                    settings, limiter, revision IDs
    db/                      Base, session factory, model registry
    modules/<feature>/       router, schemas, models, service
  alembic/                   async migration environment
frontend/
  src/
    components/ui/           shadcn-owned primitives
    features/<feature>/      app features
    lib/                     API client, cn helper
```

Rules:

- A feature owns its router/schemas/models/service. Another feature imports its service, not its ORM model.
- `app/db/registry.py` is the only place that imports every model module for Alembic metadata. Add new model modules there.
- `app/api/v1/router.py` is the only composition root. Feature routers keep their own prefixes and tags.
- The frontend mirrors this with `src/features/<feature>/`; shared UI primitives stay in `src/components/ui/`.
- Extraction path: because a module already owns its HTTP, validation, persistence, and service layers, it can move to a separate package or service without a cross-module model rewrite.
