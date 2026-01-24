# Skill — Add a new Backend Feature

Tags: [backend] [feature] [custom]

## Goal
Implement a new backend feature in a fork-friendly way:
- feature lives under `backend/app/custom/features/<feature_name>/`
- it follows the feature architecture: routes → service → repository → model
- it uses interfaces from `shared/interfaces/` when possible
- it is self-contained and testable

## When to use
- Adding a new API endpoint or business logic in the backend
- Extending backend functionality for a client
- Creating a new domain module

## Preconditions
- The feature name is agreed and follows naming conventions (snake_case).
- Database models are identified (if needed).
- External integrations are identified (if needed).

## Steps (MANDATORY ORDER)

### 1) Create feature directory structure
Create:
`backend/app/custom/features/<feature_name>/`
- `__init__.py`
- `routes.py` (FastAPI endpoints)
- `schemas.py` (Pydantic models)
- `service.py` (business logic)
- `repository.py` (data access, optional)
- `models.py` (SQLAlchemy models, optional)
- `tasks.py` (Celery tasks, optional)
- `README.md` (feature documentation)

### 2) Define schemas (Pydantic)
- Create request/response models in `schemas.py`.
- Use descriptive names and proper types.
- Include validation rules.

### 3) Define models (SQLAlchemy, if needed)
- Create models in `models.py` if database tables are needed.
- Follow SQLAlchemy 2.0 conventions.
- **CRITICAL**: After creating/modifying models, create Alembic migration (see `add_database_migration`).

### 4) Implement repository (optional)
- Create `repository.py` if data access is needed.
- Extend `BaseRepository` from `shared/repositories/`.
- Keep data access logic isolated.

### 5) Implement service (business logic)
- Create `service.py` with business logic.
- Use dependency injection for repositories and external services.
- Keep business logic independent of framework details.

### 6) Implement routes (API endpoints)
- Create `routes.py` with FastAPI endpoints.
- Use dependency injection for services.
- Follow REST conventions.
- Include proper error handling.

### 7) Register feature router
- Add router to `backend/app/custom/features/__init__.py`:
```python
from app.custom.features.<feature_name>.routes import router as <feature_name>_router
routers.append(<feature_name>_router)
```

### 8) Add Celery tasks (if needed)
- Create `tasks.py` if background tasks are needed.
- Use `@celery_app.task` decorator.
- Tasks are auto-discovered by Celery.

### 9) Add tests
- Unit tests for service logic (mock dependencies).
- Integration tests for API endpoints.
- Test error cases and edge cases.

### 10) Add documentation
- Update `README.md` with:
  - Feature purpose
  - API endpoints
  - Usage examples
  - Dependencies

## Validation
- Feature can be imported and router registered.
- API endpoints are accessible and return expected responses.
- Unit tests pass.
- Integration tests pass (if applicable).
- Database migrations created and applied (if models added).
- No circular dependencies.
- Type hints are complete (Python 3.11+).

## Common mistakes (avoid)
- Putting business logic in routes (should be in service).
- Creating models without migrations.
- Hardcoding values (use config or env vars).
- Skipping type hints.
- Creating features in `core/features/` instead of `custom/features/`.

## Troubleshooting
- If database models are out of sync → use `add_database_migration`.
- If external service integration needed → use `add_integration`.
- If background tasks needed → add `tasks.py` following Celery patterns.
