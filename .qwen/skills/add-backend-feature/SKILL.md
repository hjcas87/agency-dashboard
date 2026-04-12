---
name: add-backend-feature
description: Implement a new backend API feature in the custom/features directory following the repository pattern, service layer, and FastAPI conventions. Use when adding backend functionality, API endpoints, or business logic.
---

# Add Backend Feature

## When to use
- Adding a new API endpoint or business logic in the backend
- Extending backend functionality for a client
- Creating a new domain module

## Preconditions
- Feature name follows snake_case convention
- Database models are identified (if needed)
- External integrations are identified (if needed)

## Steps

### 1) Create feature directory structure
```
backend/app/custom/features/<feature_name>/
├── __init__.py
├── routes.py          # FastAPI endpoints
├── schemas.py         # Pydantic models
├── service.py         # Business logic
├── repository.py      # Data access (optional)
├── models.py          # SQLAlchemy models (optional)
├── tasks.py           # Celery tasks (optional)
└── README.md          # Feature documentation
```

### 2) Define schemas (Pydantic)
- Create request/response models in `schemas.py`
- Use descriptive names and proper types
- Include validation rules

### 3) Define models (SQLAlchemy, if needed)
- Create models in `models.py` if database tables are needed
- Follow SQLAlchemy 2.0 conventions
- **CRITICAL**: After creating models, run `add-database-migration` skill

### 4) Implement repository (optional)
- Create `repository.py` if data access is needed
- Extend `BaseRepository` from `shared/repositories/`

### 5) Implement service (business logic)
- Create `service.py` with business logic
- Use dependency injection for repositories and external services
- Keep business logic independent of framework details

### 6) Implement routes (API endpoints)
- Create `routes.py` with FastAPI endpoints
- Use dependency injection for services
- Follow REST conventions
- Include proper error handling

### 7) Register feature router
Add to `backend/app/custom/features/__init__.py`:
```python
from app.custom.features.<feature_name>.routes import router as <feature_name>_router
routers.append(<feature_name>_router)
```

### 8) Add Celery tasks (if needed)
- Create `tasks.py` if background tasks are needed
- Use `@celery_app.task` decorator

### 9) Add tests
- Unit tests for service logic (mock dependencies)
- Integration tests for API endpoints

### 10) Add documentation
- Update `README.md` with feature purpose, API endpoints, usage examples

## Validation
- Feature can be imported and router registered
- API endpoints are accessible and return expected responses
- Unit tests pass
- Database migrations created and applied (if models added)
- No circular dependencies
- Type hints complete (Python 3.11+)

## Common mistakes
- Putting business logic in routes (should be in service)
- Creating models without migrations
- Hardcoding values (use config or env vars)
- Skipping type hints
- Creating features in `core/features/` instead of `custom/features/`
