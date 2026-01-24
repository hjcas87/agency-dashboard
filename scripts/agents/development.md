# Agent Starter — Development (Web Application Boilerplate)

You are working inside the **Web Application Boilerplate** template repo.

## Operating mode (MANDATORY)
1) Select the correct **role** from `docs/agents/roles/`:
   - Default: `Feature-Developer`
   - If the task is backend architecture: `Backend-Architect`
   - If the task is frontend architecture: `Frontend-Architect`
   - If the task is reviewing changes: `Code-Reviewer`
   - If the task is solution design: `Solution-Designer`
2) Follow **AGENTS.md** and the **Skills Protocol** strictly.
3) Do NOT invent requirements. Treat `docs/solution_design/` as the single source of truth.

## Source of truth (MANDATORY)
You MUST base your work on:
- `docs/PROJECT_BRIEF.md` (if exists, for new client projects)
- `docs/solution_design/scope.md`
- `docs/solution_design/system_requirements.md`
- `docs/solution_design/assumptions_and_constraints.md`
- `docs/solution_design/user_stories/*.md`
- `docs/solution_design/diagrams/*.excalidraw`

If something is missing or ambiguous, STOP and ask for clarification.

---

## Repository boundaries (STRICT)
- Client/business logic → `backend/app/custom/features/` and `frontend/components/custom/`
- Generic features → `backend/app/core/features/` and `frontend/components/core/`
- Shared code → `backend/app/shared/` and `frontend/lib/core/`
Never put client-specific logic into `core/` or `shared/`.

---

## Dependency management (STRICT)

### Backend
This repo uses **uv** only.
- Add deps with `uv add ...` (or `uv add --dev ...`)
- Update lock with `uv lock`
- Sync with `uv sync`
Do NOT use `pip install` / `requirements.txt` / Poetry.

### Frontend
This repo uses **npm**.
- Install deps with `npm install <package>`
- Update lock automatically with `npm install`
Do NOT manually edit `package.json` versions.

---

## Coding standards (STRICT)

### Python (Backend)
- Python 3.11+
- PEP8 strictly
- No imports inside functions/methods (module-level imports only)
- No `print` (structured logging only)
- All functions/methods must have typed inputs + typed return
- Avoid `typing` generics that Python 3.11 already supports:
  - DO NOT use `List`, `Dict`, `Optional`, `Union`, etc.
  - Use `list[str]`, `dict[str, int]`, `str | None`, etc.
- Using `Protocol`, `TypeVar`, `Generic` from `typing` is allowed.

### TypeScript (Frontend)
- TypeScript strict mode
- No `any` types (use `unknown` if needed)
- Server Components by default
- Use `'use client'` only when needed (interactivity, hooks, browser APIs)

---

## Deliverable format (MANDATORY)
When implementing a feature:
1) Provide a short implementation plan.
2) List files to be created/modified.
3) Implement changes (code).
4) Provide commands to run:
   - `make format` (formatting)
   - `make lint` (linting)
   - `make test` (tests)
5) Ensure database migrations are created if models changed.

---

# Work procedure (MANDATORY ORDER)

## Step 1 — Identify target feature + user story
- Determine:
  - feature name: `<feature_name>`
  - user story file: `docs/solution_design/user_stories/<US-XXX_...>.md` (if exists)
- Extract:
  - Goal / behavior
  - Preconditions
  - Acceptance criteria
  - Error paths
  - Required API endpoints / UI components

If anything is missing → ask.

---

## Step 2 — Select required skill(s)
Apply triggers:
- Creating backend feature → use `docs/agents/skills/add_backend_feature.md`
- Creating frontend feature → use `docs/agents/skills/add_frontend_feature.md`
- Creating full-stack feature → use `docs/agents/skills/add_feature.md`
- Adding database models → `docs/agents/skills/add_database_migration.md`
- Adding external integration → `docs/agents/skills/add_integration.md`
- Adding N8N workflow → `docs/agents/skills/add_n8n_workflow.md`
- Adding Celery task → `docs/agents/skills/add_celery_task.md`

Follow skill steps in order.

---

## Step 3 — Map User Story → Feature (1:1)
Convention:
- Each user story maps to exactly one feature (backend + frontend if needed).
- Feature name should be `snake_case` and intention-revealing.

Create/modify:
- Backend: `backend/app/custom/features/<feature_name>/`
- Frontend: `frontend/components/custom/features/<feature_name>/` and `frontend/app/(private)/(custom)/<feature_name>/`

---

## Step 4 — Define schemas/models
If the feature requires data:
- Backend: Create Pydantic schemas in `schemas.py` and SQLAlchemy models in `models.py`
- Frontend: Create TypeScript types (generate from OpenAPI when possible)

Rules:
- Backend schemas must be JSON-serializable
- Database models MUST have Alembic migrations created
- Frontend types should be generated from OpenAPI schema: `npm run generate-api-types`

---

## Step 5 — Implement backend feature (if needed)
Rules:
- Feature follows: routes → service → repository → model
- Use dependency injection for services
- Keep business logic in service layer
- Use interfaces from `shared/interfaces/` when possible

Typical structure:
- `routes.py` - FastAPI endpoints
- `schemas.py` - Pydantic models
- `service.py` - Business logic
- `repository.py` - Data access (optional)
- `models.py` - SQLAlchemy models (optional)
- `tasks.py` - Celery tasks (optional)

---

## Step 6 — Implement frontend feature (if needed)
Rules:
- Use Server Components by default
- Use `'use client'` only for interactivity
- Use Server Actions for mutations
- Handle loading and error states

Typical structure:
- Components in `frontend/components/custom/features/<feature_name>/`
- Pages in `frontend/app/(private)/(custom)/<feature_name>/`
- Types in `types.ts` (if needed)
- Services in `services/` (if needed)

---

## Step 7 — Add database migrations (if models added)
- Create Alembic migration: `uv run alembic revision --autogenerate -m "Description"`
- Apply migration: `uv run alembic upgrade head`
- Verify models are synchronized with database tables

---

## Step 8 — Register feature
- Backend: Add router to `backend/app/custom/features/__init__.py`
- Frontend: Components and pages are auto-discovered by Next.js

---

## Step 9 — Tests
For each feature:
- Backend: Unit tests for service, integration tests for API endpoints
- Frontend: Component tests (if applicable)

Where:
- Backend: `backend/tests/`
- Frontend: `frontend/__tests__/` or similar (if configured)

---

## Step 10 — Verify
Commands:
- `make test` (run all tests)
- `make lint` (check code quality)
- `make format` (format code)
- `make dev` (start services and verify manually)

If it fails:
- Check error logs
- Verify database migrations applied
- Check environment variables

---

# Output checklist (MANDATORY)
Before declaring done, confirm:
- Boundaries respected (core/custom/shared)
- Typing complete (Python 3.11+ and TypeScript)
- No hardcoded values (use config/env vars)
- Database migrations created and applied (if models changed)
- Tests added/updated
- Code formatted and linted
- Feature works as expected
- User story acceptance criteria met (if applicable)
