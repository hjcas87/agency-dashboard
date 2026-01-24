# Agents Guide — Web Application Boilerplate

This repo is a reusable template for enterprise-grade web applications with frontend, backend, and automation capabilities.

Agents must follow the architecture boundaries to keep forks and customizations safe.

## Mission

Help build, extend, and maintain web applications while preserving:
- clean separation: core vs custom (frontend and backend)
- type safety: TypeScript (frontend) and Python type hints (backend)
- fork-friendly customization patterns
- production-ready code quality

## Required reading (MANDATORY)

Before proposing changes, the agent MUST read:
- `ARCHITECTURE.md`
- `docs/agents/skills/README.md`
- `docs/solution_design/README.md` (when working on solution definition)
- `docs/PROJECT_BRIEF.template.md` (when starting a new client project)

## Repository boundaries (STRICT)

### Frontend

**1) `components/core/` (stable)**
- Base UI components (shadcn/ui)
- Core feature components
- Do not add client-specific behavior here
- Changes must be generic, backward-compatible, and tested

**2) `components/custom/` (custom)**
- Client-specific components
- Custom feature components
- This is the default place for client UI components

**3) `app/actions/core/` (stable)**
- Core server actions (auth, etc.)
- Do not modify in forks

**4) `app/actions/custom/` (custom)**
- Custom server actions
- Client-specific server logic

**5) `app/api/(core)/` (stable)**
- Core API endpoints (auth, proxy)
- Do not modify in forks

**6) `app/api/(custom)/` (custom)**
- Custom API endpoints
- Client-specific API routes

**7) `app/(private)/(custom)/` (custom)**
- Custom pages for client
- All routes here are protected by `(private)/layout.tsx`

**8) `app/(private)/page.tsx` (custom)**
- Home dashboard (each fork can override)

**9) `app/(private)/layout.tsx` (stable)**
- Authentication check (do not modify in forks)

### Backend

**1) `app/core/` (stable)**
- Core features (auth, users, health, n8n)
- Core infrastructure (tasks, router)
- Do not add client-specific behavior here
- Changes must be generic, backward-compatible, and tested

**2) `app/custom/features/` (custom)**
- Client-specific features
- This is the default place to implement new features

**3) `app/shared/` (stable)**
- Shared interfaces and services
- Base repositories
- Do not add client-specific logic here

If unsure where code belongs:
- business-specific → `custom/features/`
- generic, reusable → `core/features/`
- shared utilities → `shared/`

## Agent Roles (MANDATORY)

This repository defines explicit agent roles under `docs/agents/roles/`.

### Default role

If the user does not specify a role, the agent MUST assume:
- **Feature-Developer**

This default role is defined as an alias under:
- `docs/agents/roles/default.md`

### Auto role selection

The agent MUST switch roles based on the task:
- Frontend architecture or Next.js/React decisions → `Frontend-Architect`
- Backend architecture or FastAPI decisions → `Backend-Architect`
- Reviewing changes / PR review / quality gate → `Code-Reviewer`
- Implementing new features or client changes → `Feature-Developer`
- Creating or updating solution definition docs (requirements, scope, diagrams, user stories) → `Solution-Designer`

### Role invocation rule

Before planning or editing code, the agent MUST:
1. Select the role (default or auto-selected),
2. Follow the role's priorities and constraints,
3. Apply the Skills Protocol and triggers.

## Dependency Management (STRICT)

### Backend (Python)

This repository uses **uv** as the only supported dependency manager.

Rules:
- Dependencies MUST be added using `uv add <package>`.
- The lockfile (`uv.lock`) MUST be updated using `uv lock`.
- Do NOT use:
  - `pip install`
  - `requirements.txt`
  - `poetry add`
- Do NOT edit `pyproject.toml` dependencies manually.
- Dependencies MUST be installed using `uv sync` (uses `uv.lock`).

Whenever dependencies are added, removed, or upgraded:
1. Run `uv add <package>` (or `uv add --dev <package>`).
2. Run `uv lock`.
3. Commit both `pyproject.toml` and `uv.lock`.

### Frontend (Node.js)

This repository uses **npm** for package management.

Rules:
- Dependencies MUST be added using `npm install <package>`.
- The lockfile (`package-lock.json`) is automatically updated.
- Do NOT manually edit `package.json` version numbers.
- Use `npm install` to sync dependencies.

Violations of these rules are considered **Blockers** in review.

## Skills Protocol (MANDATORY)

Skills are defined under `docs/agents/skills/`.

For any task, the agent MUST:
1. Identify the task category.
2. Check if a matching skill exists.
3. Follow the skill steps in order.
4. Perform the skill "Validation" before declaring completion.
5. Only deviate if explicitly instructed.

If multiple skills apply, follow this priority:
**safety/debug → boundaries → implementation**

Skills are identified by **name**, not by numeric order.

## Skill Triggers (STRICT)

The agent MUST invoke the corresponding skill when any of the following occurs:

### Solution Design
- Creating or updating solution definition, scope, diagrams, or user stories →
  `solution_design.md` (Role: Solution Designer)

### Features
- Adding a new backend feature →
  `add_backend_feature.md`
- Adding a new frontend feature →
  `add_frontend_feature.md`
- Adding a new full-stack feature →
  `add_feature.md`

### Integrations
- Adding a new external service integration →
  `add_integration.md`
- Adding a new N8N workflow →
  `add_n8n_workflow.md`
- Adding Celery background tasks →
  `add_celery_task.md`

### Database
- Modifying SQLAlchemy models →
  `add_database_migration.md`

### Client Setup
- Creating a new client fork →
  `setup_new_client_fork.md`

### Reviews / Quality Gate
- Reviewing changes, PRs, or acting as a quality gate →
  `review_feature.md`

### Deployment
- Preparing deployment, migrations, or release →
  `deploy.md`

### Skills Maintenance
- Adding or updating skills or conventions →
  `add_or_update_skill.md`

### Enforcement
- When a skill is triggered, its steps MUST be followed in order.
- Validation MUST be completed before declaring success.
- If a step cannot be executed, the agent must stop and ask for clarification.

## Skill Trigger Map

| Situation | Skill |
|---|---|
| Define solution requirements, scope, diagrams, user stories | solution_design |
| Add new backend feature | add_backend_feature |
| Add new frontend feature | add_frontend_feature |
| Add new full-stack feature | add_feature |
| Add external service integration | add_integration |
| Add N8N workflow | add_n8n_workflow |
| Add Celery background task | add_celery_task |
| Modify database models | add_database_migration |
| Create new client fork | setup_new_client_fork |
| Review changes / PR / quality gate | review_feature |
| Prepare deployment or release | deploy |
| Add or update skills/conventions | add_or_update_skill |

Skipping an existing skill is considered an error.

Skills must follow the convention documented in:
- `docs/agents/skills/README.md`

## Coding rules (STRICT)

### General
1. Follow project conventions strictly (naming, spacing, imports, formatting).
2. No hardcoded values; use configuration files or environment variables.
3. Use structured logging (no `print` statements).
4. All imports must be at module level (no imports inside functions/methods).

### Python (Backend)
5. Python version is **3.11+**.
6. Do NOT use types imported from `typing`:
   - ❌ `List`, `Dict`, `Tuple`, `Set`, `Optional`, `Union`
   - ❌ `from typing import ...`
7. Use built-in generics and modern syntax:
   - ✅ `list[str]`
   - ✅ `dict[str, int]`
   - ✅ `str | None`
8. All functions and methods MUST have:
   - typed inputs
   - typed return value (no implicit `Any`)
9. Formatting: Black (line-length=100), isort (profile=black), Ruff (linting)
10. Database models MUST be synchronized with database tables via Alembic migrations

### TypeScript (Frontend)
11. TypeScript strict mode enabled.
12. No `any` types (use `unknown` if needed).
13. Use Server Components by default.
14. Use `'use client'` only when needed (interactivity, hooks, browser APIs).
15. Generate API types from OpenAPI schema: `npm run generate-api-types`
16. Formatting: Prettier (project config)

### Error handling
17. Exceptions must not be silently swallowed.
18. Provide meaningful error messages.
19. Log errors appropriately (structured logging).

Violations of these rules are considered blockers during review.

## Fork-friendly development workflow

When creating a new client project:

1. **Analyst creates PROJECT_BRIEF** → Copy `docs/PROJECT_BRIEF.template.md` to `docs/PROJECT_BRIEF.md`
2. **Cursor generates solution_design/** → Based on PROJECT_BRIEF
3. **Refine with client** → Iterate until approved
4. **Cursor generates code** → Based on approved solution design
5. **Implement features** → In `custom/features/` (backend) and `custom/` (frontend)
6. **Do not modify core** → Unless strictly necessary and backward-compatible

## Definition of Done

- Code compiles and passes type checks (TypeScript + Python).
- Unit tests exist for pure logic.
- Integration tests exist for API endpoints and database operations.
- No architecture boundary violations (core vs custom).
- Database models are synchronized with tables (Alembic migrations).
- Documentation updated if needed.

## Commands (recommended)

### Development

**Backend:**
```bash
# Install dependencies
cd backend && uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app --cov-report=html

# Format code
uv run black app && uv run isort app

# Create database migration
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

**Frontend:**
```bash
# Install dependencies
cd frontend && npm install

# Run development server
npm run dev

# Build for production
npm run build

# Generate API types
npm run generate-api-types

# Format code
npm run format
```

**Infrastructure:**
```bash
# Start all services
make dev

# Stop all services
make down

# View logs
make logs

# Run tests
make test
```

## Project Brief Workflow

1. **Analyst meets with client** → Discusses needs and requirements
2. **Create PROJECT_BRIEF** → Copy `docs/PROJECT_BRIEF.template.md` to `docs/PROJECT_BRIEF.md` in the client fork
3. **Fill PROJECT_BRIEF** → Document agreed needs, scope, integrations, constraints
4. **Cursor reads PROJECT_BRIEF** → Generates `docs/solution_design/` documentation
5. **Refine solution_design** → With client and analyst until approved
6. **Cursor generates code** → Based on approved solution design and diagrams

The PROJECT_BRIEF is the starting point for all client-specific development.
