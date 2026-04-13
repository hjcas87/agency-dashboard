# QWEN.md — Mendri Agency Dashboard

## Project Overview

**Mendri Agency Dashboard** is a base project for managing agency operations — clients, budgets, billing, and project tracking. It combines a Next.js frontend, FastAPI backend, PostgreSQL database, RabbitMQ message broker, Celery background workers, and N8N workflow automation.

### Architecture Philosophy

The project follows a **core/custom separation** pattern:
- **`core/`** — Stable, generic modules (auth, users, health, N8N integration). Should NOT be modified.
- **`custom/`** — Project-specific features. Safe to modify per need.
- **`shared/`** — Shared interfaces, base services, and repositories.

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16+ (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.12+, SQLAlchemy 2.0, Alembic, Pydantic |
| **Database** | PostgreSQL 15 |
| **Message Broker** | RabbitMQ (Celery) |
| **Background Tasks** | Celery + Flower (monitoring) |
| **Automation** | N8N (self-hosted) |
| **Reverse Proxy** | Nginx |
| **Package Managers** | `uv` (Python), `npm` (Node.js) |

## Key Commands

### Development

```bash
# Start infrastructure (PostgreSQL, RabbitMQ, N8N, Celery)
make dev

# Stop services
make down

# View logs
make logs

# Run backend
cd backend && uv run uvicorn app.main:app --reload

# Run frontend
cd frontend && npm run dev
```

### Code Quality

```bash
# Format backend
cd backend && uv run black app && uv run isort app

# Format frontend
cd frontend && npm run format

# Run tests
make test
```

### Pre-commit

```bash
make pre-commit-install
pre-commit run --all-files
```

## Coding Conventions

### Python (Backend)

- Python 3.12+ only
- Use built-in generics: `list[str]`, `dict[str, int]`, `str | None`
- DO NOT import from `typing` (no `List`, `Dict`, `Optional`, `Union`)
- All functions must have typed inputs and return values
- No imports inside functions — module-level only
- Structured logging only — no `print()`
- Database models must sync via Alembic migrations

### TypeScript (Frontend)

- Strict mode enabled
- No `any` types (use `unknown` if needed)
- Server Components by default; `'use client'` only when necessary
- Generate API types: `npm run generate-api-types`

### General

- No hardcoded values — use config/env vars
- Meaningful error messages
- English for all code, comments, and docstrings
- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`

## Agent Roles & Skills

AI agents MUST follow roles and skills defined in `docs/agents/`:

- **Roles**: `docs/agents/roles/` — Agent personas (default: Feature-Developer)
- **Skills**: `docs/agents/skills/` — Step-by-step procedures

**Mandatory reading before any work:**
1. `ARCHITECTURE.md`
2. `docs/agents/skills/README.md`
3. `docs/solution_design/` (when working on solution definition)
4. `docs/PROJECT_BRIEF.template.md` (when starting a new client project)

## Git Workflow

### Core Changes
1. Work in `dev` branch
2. Review and test in `dev`
3. Merge `dev` → `main`

### Custom Changes
- Commit directly to client branch
- Independent from `dev`/`main` workflow

## Services (Development)

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| N8N | http://localhost:5678 |
| RabbitMQ Management | http://localhost:15672 |
| Flower (Celery) | http://localhost:5555 |

## New Feature Structure

### Backend (Custom Feature)

```
backend/app/custom/features/<feature_name>/
├── __init__.py
├── routes.py          # FastAPI endpoints
├── schemas.py         # Pydantic schemas
├── service.py         # Business logic
├── models.py          # SQLAlchemy models (optional)
└── tasks.py           # Celery tasks (optional)
```

### Frontend (Custom Feature)

- **Pages**: `frontend/app/(private)/(custom)/<feature>/page.tsx`
- **Components**: `frontend/components/custom/features/<feature>/`
- **Services**: `frontend/lib/custom/features/<feature>/`
