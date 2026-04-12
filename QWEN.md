# QWEN.md — Automation Warehouse

## Project Overview

**Automation Warehouse** is a reusable, enterprise-grade boilerplate for building full-stack web applications with AI-driven automation capabilities. It combines a Next.js frontend, FastAPI backend, PostgreSQL database, RabbitMQ message broker, Celery background workers, and N8N workflow automation — all orchestrated via Docker Compose.

### Architecture Philosophy

The project follows a **core/custom separation** pattern:
- **`core/`** — Stable, generic, reusable modules (auth, users, health, N8N integration). Should NOT be modified in client forks.
- **`custom/`** — Client-specific features and customizations. Safe to modify per project.
- **`shared/`** — Shared interfaces, base services, and repositories used by both core and custom.

This enables fork-friendly development: update the core without breaking client-specific customizations.

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15+ (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy 2.0, Alembic, Pydantic |
| **Database** | PostgreSQL 15 |
| **Message Broker** | RabbitMQ (Celery) |
| **Background Tasks** | Celery + Flower (monitoring) |
| **Automation** | N8N (self-hosted, with PostgreSQL backend) |
| **Reverse Proxy** | Nginx |
| **Package Managers** | `uv` (Python), `npm` (Node.js) |

## Repository Structure

```
.
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── core/               # Core features (auth, users, health, n8n) — DO NOT MODIFY
│   │   ├── custom/             # Client-specific features — SAFE TO MODIFY
│   │   └── shared/             # Shared interfaces, services, repositories
│   ├── alembic/                # Database migrations
│   └── tests/                  # Backend tests
├── frontend/                   # Next.js application
│   ├── app/                    # App Router
│   │   ├── (auth)/            # Public auth routes
│   │   ├── (private)/         # Protected routes
│   │   ├── api/(core)/        # Core API routes
│   │   ├── api/(custom)/      # Custom API routes
│   │   ├── actions/core/      # Core server actions
│   │   └── actions/custom/    # Custom server actions
│   ├── components/
│   │   ├── core/              # Base UI components — DO NOT MODIFY
│   │   └── custom/            # Client-specific components — SAFE TO MODIFY
│   └── lib/                   # Utilities and API clients
├── automation/                 # N8N workflows
├── nginx/                      # Nginx configuration
├── docs/
│   ├── agents/                 # AI agent roles, skills, and protocols
│   └── solution_design/        # Solution design templates
├── docker-compose.yml          # Development environment
└── docker-compose.prod.yml     # Production environment (Traefik-ready)
```

## Key Commands

### Development

```bash
# Start all infrastructure services (PostgreSQL, RabbitMQ, N8N, Celery, Nginx)
make dev

# Stop all services
make down

# View logs
make logs

# Run backend locally
cd backend && uv run uvicorn app.main:app --reload

# Run frontend locally
cd frontend && npm run dev
```

### Testing

```bash
# All backend tests
make test

# Unit tests only (fast)
make test-unit

# Integration tests only
make test-integration

# Tests with coverage
make test-cov
```

### Code Quality

```bash
# Lint backend
cd backend && uv run black --check app && uv run isort --check-only app && uv run ruff check app

# Format backend
cd backend && uv run black app && uv run isort app && uv run ruff check --fix app

# Lint frontend
cd frontend && npm run lint

# Format frontend
cd frontend && npm run format
```

### Database

```bash
# Run migrations
make db-migrate

# Create new migration
make db-revision MESSAGE="description"
```

### API Types (Frontend)

```bash
# Generate TypeScript types from OpenAPI schema
make frontend-api-types
```

### Pre-commit

```bash
# Install hooks
make pre-commit-install

# Run on all files
make pre-commit-run
```

## Coding Conventions

### Python (Backend)

- **Python 3.11+** only
- Use built-in generics: `list[str]`, `dict[str, int]`, `str | None`
- **DO NOT** import from `typing` (no `List`, `Dict`, `Optional`, `Union`, etc.)
- All functions MUST have typed inputs and return values
- No imports inside functions — module-level only
- Formatters: Black (line-length=100), isort (profile=black), Ruff (linting)
- Structured logging only — no `print()` statements
- Database models MUST be synced via Alembic migrations

### TypeScript (Frontend)

- Strict mode enabled
- No `any` types (use `unknown` if needed)
- Server Components by default; `'use client'` only when necessary
- Generate API types from OpenAPI: `npm run generate-api-types`
- Formatters: Prettier (project config)

### General

- No hardcoded values — use config/env vars
- Meaningful error messages
- English for all code, comments, and docstrings
- Follow conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, etc.

## Agent Roles & Skills

This repository defines explicit AI agent behavior under `docs/agents/`:

- **Roles**: `docs/agents/roles/` — Agent personas (default: Feature-Developer)
- **Skills**: `docs/agents/skills/` — Step-by-step procedures for tasks
- **Protocols**: Agents MUST follow the Skills Protocol for all task categories

Key skills include: `add_backend_feature`, `add_frontend_feature`, `add_integration`, `add_database_migration`, `review_feature`, `deploy`, and more.

**Mandatory reading before any work:**
1. `ARCHITECTURE.md`
2. `docs/agents/skills/README.md`
3. `docs/solution_design/README.md` (when working on solution definition)
4. `docs/PROJECT_BRIEF.template.md` (when starting a new client project)

## Git Workflow

### Core Changes — MUST use `dev` branch

1. Work in `dev` branch or feature branch from `dev`
2. Review and test in `dev`
3. Merge `dev` → `main` (only after approval)
4. Update client branches from `main`

**NEVER** commit core changes directly to `main`.

### Custom Changes — Client branches

- Commit directly to client branch (`crm-prego`, `crm-artistealo`, etc.)
- Independent from `dev`/`main` workflow

## New Feature Structure

### Backend (Custom Feature)

```
backend/app/custom/features/<feature_name>/
├── __init__.py
├── routes.py          # FastAPI endpoints
├── schemas.py         # Pydantic schemas
├── service.py         # Business logic
├── repository.py      # Data access (optional)
├── models.py          # SQLAlchemy models (optional)
├── tasks.py           # Celery tasks (optional)
└── README.md          # Feature documentation
```

### Frontend (Custom Feature)

- **Pages**: `frontend/app/(private)/(custom)/<feature>/page.tsx`
- **Components**: `frontend/components/custom/features/<feature>/`
- **Services**: `frontend/lib/custom/features/<feature>/`

## Services (Development)

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| N8N | http://localhost:5678 |
| RabbitMQ Management | http://localhost:15672 |
| Flower (Celery) | http://localhost:5555 |
| Nginx | http://localhost:80 |

## Dependency Management

### Backend (Python — via `uv`)

```bash
# Add dependency
uv add <package>

# Lock dependencies
uv lock

# Install dependencies
uv sync
```

### Frontend (Node.js — via `npm`)

```bash
# Add dependency
npm install <package>

# Install dependencies
npm install
```

## Documentation Language Rules

- **Solution Design docs** (`docs/solution_design/`): **Spanish** (for client review)
- **Technical docs** (READMEs, ARCHITECTURE.md, AGENTS.md): **English**
- **All code and comments**: **English**
