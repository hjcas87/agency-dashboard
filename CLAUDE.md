# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Required reading before non-trivial changes

`AGENTS.md` and `ARCHITECTURE.md` define strict rules that override generic defaults. Skim them before planning code changes — they specify the role to assume, skills to invoke, and the core/custom boundaries enforced in review.

Skills under `docs/agents/skills/` (e.g. `add_backend_feature.md`, `add_database_migration.md`, `add_frontend_feature.md`, `review_feature.md`) are mandatory step-by-step procedures for the matching task category. When a skill matches the task, follow its steps in order and run its Validation section before declaring done.

## Language conventions (non-obvious)

- **Code, comments, docstrings, identifiers**: English (Python and TypeScript).
- **`docs/solution_design/`**: Spanish — these are client-facing.
- **Chat replies to the user**: Spanish (per `.cursor/rules.md`). Other technical docs (`README.md`, `ARCHITECTURE.md`, `AGENTS.md`) stay in English.

## Architecture: core vs custom (strict boundary)

Both `backend/app/` and `frontend/` are split into a stable `core/` zone and a modifiable `custom/` zone. This split is enforced by `.gitattributes` merge drivers so client branches can pull `main` without conflicts:

- `core/**` paths are marked `merge=theirs` — client branches always take main's version.
- `custom/**` paths are marked `merge=ours` — client branches keep their own version.

Practical consequence: **never put client-specific logic in `core/`**, and never mass-rename across the boundary. If a feature could not benefit multiple clients, it belongs in `custom/`.

### Backend layout

```
backend/app/
├── core/features/        # auth, users, health, n8n  (stable, do not modify in forks)
├── core/router.py        # aggregates core + custom routers
├── core/tasks/           # Celery app config (celery_app.py)
├── custom/features/      # client features: clients, proposals, pdf, email
├── shared/               # interfaces, services, repositories, pdf, email
├── models.py             # central import of ALL SQLAlchemy models (must list every model)
└── main.py               # FastAPI app factory; mounts /uploads/{path} for served files
```

Custom routers are registered in `backend/app/custom/features/__init__.py::get_custom_routers()` — adding a new feature router requires editing that file. New SQLAlchemy models must also be imported in `backend/app/models.py` so relationships resolve before `Base.metadata.create_all()`.

Each feature follows the same shape: `routes.py` + `schemas.py` + `service.py` + optional `repository.py`, `models.py`, `tasks.py`. Celery tasks live **inside the feature** (`<feature>/tasks.py`), never in a centralized module — `autodiscover_tasks` finds them.

### Frontend layout (Next.js App Router, route groups)

```
frontend/
├── app/(auth)/                  # public: login, reset-password
├── app/(private)/layout.tsx     # CORE: auth check (do not modify in forks; do NOT add ServerAuthGuard here — middleware already protects)
├── app/(private)/page.tsx       # custom home (per-fork override)
├── app/(private)/(custom)/      # custom protected pages: clients, invoices, pdf-templates, proposals, settings
├── app/api/(core)/              # core API routes: auth, proxy
├── app/api/(custom)/            # custom API routes
├── app/actions/{core,custom}/   # server actions, split by zone
├── components/{core,custom}/
└── lib/{core,custom,shared,hooks}/
```

API types are generated from the backend's OpenAPI schema into `frontend/lib/api/types.ts` via `npm run generate-api-types` — re-run after backend schema changes.

## Database rule (critical)

SQLAlchemy models and DB tables MUST stay in sync via Alembic. Workflow: edit model → `alembic revision --autogenerate -m "..."` → review the generated migration → `alembic upgrade head`. Never edit a model without producing a migration; never edit the DB by hand. Also add the new model's import to `backend/app/models.py`.

In `DEVELOPMENT` mode (`settings.ENVIRONMENT`), `main.py` calls `Base.metadata.create_all()` on startup — this masks missing migrations locally, so verify Alembic still reflects reality before committing.

## Auth & middleware (frontend gotchas)

These are real bugs the team has hit (from `.cursor/rules.md`); they will trip you up if you don't know them:

- The middleware verifies **only that the auth cookie exists**, not that the token is valid. Do not add token validation in middleware — it causes redirect loops when an expired token is present.
- Do not redirect away from `/login` when a cookie is present. The login page itself handles invalid-token cases.
- `(private)/layout.tsx` already enforces auth. Do not wrap children in `ServerAuthGuard` — it loops with the middleware.
- Cookies can only be modified inside Server Actions or Route Handlers, never in plain Server Components.

## Commands

All make targets are `cd`-aware (they call into `backend/` or `frontend/` themselves). The Makefile is the canonical source — `make help` lists everything.

### Daily dev loop

```bash
make dev           # docker-compose up postgres only (run backend + frontend manually)
make dev-full      # also brings up RabbitMQ, N8N, Celery worker/beat/flower, nginx
make down
make logs

# Backend (separate terminal): cd backend && uv run uvicorn app.main:app --reload
# Frontend (separate terminal): cd frontend && npm run dev
```

### Tests

```bash
make test                  # all backend tests via pytest
make test-unit             # pytest -m unit
make test-integration      # pytest -m integration
make test-cov              # with coverage (pyproject enforces --cov-fail-under=80)

# Single test:
cd backend && uv run pytest tests/path/to/test_file.py::TestClass::test_name
```

Pytest markers defined in `pyproject.toml`: `unit`, `integration`, `e2e`, `performance`, `slow`, `external`, `kafka`, `n8n`, `database`. Coverage gate is **80%** and is enforced by `addopts` — failing tests below that threshold fails CI.

### Lint / format

```bash
make lint     # backend: black --check + isort --check + ruff; frontend: next lint + prettier --check
make format   # auto-fix both sides
make pre-commit-install
```

### Database migrations

```bash
# Local (docker-compose):
make db-revision MESSAGE="add foo column"
make db-migrate

# Or directly:
cd backend && uv run alembic revision --autogenerate -m "..."
cd backend && uv run alembic upgrade head
```

### Frontend API types

```bash
make frontend-api-types   # hits localhost:8000/openapi.json — backend must be running
```

### Deployment (production server)

```bash
make deploy                                    # git pull, build, up, run migrations
make deploy-create-user EMAIL=... NAME=... PASSWORD=...   # bootstrap superuser
make deploy-logs
make deploy-migrate
```

`deploy` uses `docker-compose.deploy.yml` (Traefik-fronted). `make prod` is a separate `docker-compose.prod.yml` flow.

## Dependency rules (strict — review blockers)

- **Backend**: `uv` only. Add via `uv add <pkg>` (or `uv add --dev <pkg>`), then `uv lock`, then commit both `pyproject.toml` and `uv.lock`. Never use `pip install`, `requirements.txt`, or hand-edit `pyproject.toml` deps.
- **Frontend**: `npm install <pkg>`. Do not hand-edit version numbers in `package.json`.

## Python style (enforced by tooling, but easy to forget)

- Python 3.11+. Use built-in generics: `list[str]`, `dict[str, int]`, `str | None`.
- Do **not** import `List`, `Dict`, `Tuple`, `Set`, `Optional`, `Union` from `typing`. `Any`, `Callable`, `TypeVar`, `Generic` are still fine.
- All functions/methods need typed parameters and a typed return.
- All imports at module level — no imports inside functions.
- Use structured logging via `app.core.logging_config.get_logger(__name__)`. No `print`.
- Black line-length 100, isort profile=black, ruff for lint.

## TypeScript style

- Strict mode is on. No `any` (use `unknown`).
- Server Components by default; reach for `'use client'` only when you need interactivity, hooks, or browser APIs.
- Generate API types from OpenAPI rather than hand-typing backend response shapes.

## Git workflow (core changes only)

Core changes — anything under `backend/app/core/`, `backend/app/shared/`, `frontend/components/core/`, `frontend/app/api/(core)/`, `frontend/app/actions/core/`, or `frontend/app/(private)/layout.tsx` — must land on `dev` first, get reviewed, then merge `dev → main`. Never push core changes straight to `main`. Custom changes can go directly to the relevant client branch.
