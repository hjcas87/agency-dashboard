# Architecture — Web Application Boilerplate

## Purpose

This repository is a reusable, dev-first template for building enterprise-grade web applications with frontend, backend, and automation capabilities.

It is designed to be forked per client/project while keeping a stable core and allowing safe customization.

Key properties:
- Full-stack web application (Next.js frontend + FastAPI backend)
- Modular architecture with clear core/custom separation
- Automation-ready (N8N integration, Celery background tasks)
- Fork-friendly: custom code lives in dedicated areas; core stays stable
- Production-ready infrastructure (Docker, PostgreSQL, Kafka)

## Governance (roles, skills, and solution docs)

- Agent behavior and enforcement rules: `AGENTS.md`
- Skills and procedures: `docs/agents/skills/`
- Roles and responsibilities: `docs/agents/roles/`
- Project brief template: `docs/PROJECT_BRIEF.template.md`
- Client-agreed functional definition (before development): `docs/solution_design/`

## Core principles

1. **Core/Custom Separation**: Generic, reusable code in `core/`. Client-specific code in `custom/`.
2. **Feature-Based Architecture**: Each feature is self-contained (routes, schemas, service, repository, models, tasks).
3. **Fork Safety**: Client-specific changes should not modify core unless unavoidable.
4. **Type Safety**: Full TypeScript (frontend) and Python type hints (backend).
5. **Database Synchronization**: SQLAlchemy models MUST be synchronized with database tables via Alembic migrations.
6. **Testing**: Maintain > 80% test coverage, follow TDD principles.

## Repository layout

```
.
├── frontend/                    # Next.js application
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Route group: Public auth routes
│   │   │   ├── login/
│   │   │   └── reset-password/
│   │   ├── (private)/         # Route group: Protected routes
│   │   │   ├── layout.tsx     # Core - Auth check (NOT modifiable)
│   │   │   ├── page.tsx       # Custom - Home (each fork can override)
│   │   │   └── (custom)/      # Core - Directory for custom routes
│   │   │       └── [pages]    # Custom - Client-specific pages
│   │   ├── api/               # API routes
│   │   │   ├── (core)/        # Core API endpoints (NOT modifiable)
│   │   │   │   ├── auth/      # Authentication endpoints
│   │   │   │   └── proxy/     # Generic proxy
│   │   │   └── (custom)/      # Custom API endpoints (modifiable)
│   │   ├── actions/           # Server Actions
│   │   │   ├── core/          # Core actions (NOT modifiable)
│   │   │   └── custom/        # Custom actions (modifiable)
│   │   └── layout.tsx        # Root layout
│   ├── components/            # React components
│   │   ├── core/              # Core components (NOT modifiable)
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   └── features/      # Core feature components
│   │   └── custom/             # Custom components (modifiable)
│   │       └── features/       # Custom feature components
│   └── lib/                   # Utilities
│       ├── core/              # Core utilities (NOT modifiable)
│       └── custom/             # Custom utilities (modifiable)
│
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── core/               # Core modules (NOT modifiable)
│   │   │   ├── features/       # Core features (auth, users, health, n8n)
│   │   │   │   ├── auth/
│   │   │   │   │   ├── routes.py
│   │   │   │   │   ├── schemas.py
│   │   │   │   │   ├── service.py
│   │   │   │   │   ├── models.py
│   │   │   │   │   └── tasks.py  # Celery tasks (if needed)
│   │   │   │   └── n8n/
│   │   │   ├── tasks/          # Celery configuration
│   │   │   │   └── celery_app.py
│   │   │   └── router.py       # Main router
│   │   ├── custom/             # Custom modules (modifiable)
│   │   │   └── features/       # Custom features
│   │   │       └── <feature>/
│   │   │           ├── routes.py
│   │   │           ├── schemas.py
│   │   │           ├── service.py
│   │   │           ├── repository.py
│   │   │           ├── models.py
│   │   │           └── tasks.py
│   │   └── shared/             # Shared code
│   │       ├── interfaces/      # Interfaces (IMessageBroker, IEmailService)
│   │       ├── services/       # Shared services (N8NService, EmailService)
│   │       └── repositories/   # BaseRepository
│   └── alembic/                # Database migrations
│
├── automation/                 # N8N workflows
│   └── workflows/             # Exported N8N workflows
│
├── docs/                       # Documentation
│   ├── agents/                 # Agent roles and skills
│   ├── solution_design/        # Solution design templates
│   └── PROJECT_BRIEF.template.md  # Template for project brief
│
└── docker-compose.yml          # Development environment
```

## Development workflow

### Creating a new client fork

1. **Analyst meets with client** → Agrees on high-level needs
2. **Create PROJECT_BRIEF** → Copy `docs/PROJECT_BRIEF.template.md` to `docs/PROJECT_BRIEF.md` and fill it
3. **Cursor generates solution_design/** → Based on PROJECT_BRIEF
4. **Refine with client** → Iterate on solution design until approved
5. **Cursor generates code** → Based on approved solution design

### Adding a new feature

**Backend:**
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

**Frontend:**
- Pages: `frontend/app/(private)/(custom)/<feature>/page.tsx`
- Components: `frontend/components/custom/features/<feature>/`
- Services: `frontend/lib/custom/features/<feature>/`

## Fork strategy (how to avoid breaking downstream forks)

### Stable zone (do not modify in forks)

- `frontend/components/core/` - Base UI components
- `frontend/app/actions/core/` - Core server actions
- `frontend/app/api/(core)/` - Core API endpoints
- `frontend/app/(private)/layout.tsx` - Private layout
- `backend/app/core/` - Core features and infrastructure
- `backend/app/shared/` - Shared interfaces and services

**Rule**: If a change cannot benefit multiple clients, it does not belong in `core/`.

### Custom zone (safe to change)

- `frontend/components/custom/` - Custom components
- `frontend/app/(private)/(custom)/` - Custom pages
- `frontend/app/actions/custom/` - Custom server actions
- `frontend/app/api/(custom)/` - Custom API endpoints
- `backend/app/custom/features/` - Custom features

### Extending core without modifying it

- Create new features in `custom/features/`
- Use interfaces from `shared/interfaces/`
- Implement services in `shared/services/`
- Use dependency injection for flexibility

If a core change is unavoidable:
- Keep it backward compatible
- Document it
- Add tests
- Commit to `main` first, then update client branches

## Testing strategy

- **Unit tests**: Pure logic, services, utilities (fast, no external dependencies)
- **Integration tests**: API endpoints, database operations, external services (mocked)
- **E2E tests**: Full user flows (optional, for critical paths)
- **Coverage target**: > 80%

## Database strategy

- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Critical rule**: Models MUST be synchronized with database tables
- **Workflow**: Modify model → Create Alembic migration → Run migration → Verify sync

## Deployment strategy

- **Development**: Docker Compose (all services)
- **Production**: Docker Compose with Traefik labels
- **Services**: Frontend (Next.js), Backend (FastAPI), PostgreSQL, Kafka, N8N, Celery, Nginx

## Technology stack

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Language**: Python 3.11+
- **Package Manager**: uv

### Infrastructure
- **Database**: PostgreSQL
- **Message Broker**: Kafka
- **Background Tasks**: Celery
- **Automation**: N8N (self-hosted)
- **Reverse Proxy**: Nginx

## Python standards

- Python 3.11+ only
- Use built-in generics (`list[str]`, `dict[str, int]`) and unions (`str | None`)
- Do NOT import types from `typing` (except `Any`, `Callable`, `TypeVar`, `Generic`)
- All functions and methods must have typed inputs and return values
- No imports inside functions/methods; module-level imports only
- Formatting: Black (line-length=100), isort (profile=black), Ruff (linting)

## TypeScript standards

- Strict mode enabled
- No `any` types (use `unknown` if needed)
- Generate API types from OpenAPI schema
- Use Server Components by default
- Use `'use client'` only when needed (interactivity, hooks, browser APIs)

## Dependency management

### Backend (Python)
- Use `uv` for package management
- `pyproject.toml` defines dependencies
- `uv.lock` ensures reproducible builds
- Commands: `uv add <package>`, `uv lock`, `uv sync`

### Frontend (Node.js)
- Use `npm` for package management
- `package.json` defines dependencies
- `package-lock.json` ensures reproducible builds
- Commands: `npm install`, `npm run <script>`

## Git workflow

### Core changes
1. Identify changes in `core/`
2. Commit to current branch (temporary)
3. Switch to `main` and cherry-pick/merge
4. Return to client branch and merge from `main`
5. `.gitattributes` automatically resolves conflicts

### Custom changes
- Commit directly to client branch
- No need to go through `main`

## Documentation updates

When making core changes:
- Update `ARCHITECTURE.md` if structure changes
- Update `AGENTS.md` if workflows/conventions change
- Update relevant skills/roles if procedures change
- Only update if the change is significant and affects how agents/developers work
