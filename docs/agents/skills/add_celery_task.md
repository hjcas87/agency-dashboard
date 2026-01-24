# Skill — Add Celery Background Task

Tags: [celery] [task] [background] [async]

## Goal
Add a Celery background task within a feature.

**IMPORTANT**: Tasks are auto-contained within each feature. Each feature that needs background tasks has its own `tasks.py`.

## When to use
- Adding long-running operations.
- Adding async processing.
- Adding scheduled tasks.

## Preconditions
- Feature exists under `custom/features/<feature_name>/`.
- Task requirements are understood.

## Steps (MANDATORY ORDER)

### 1) Create tasks.py in feature
- Create `backend/app/custom/features/<feature_name>/tasks.py`.
- Import `celery_app` from `app.core.tasks.celery_app`.

### 2) Define task
```python
from app.core.tasks.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def my_task(self, param1: str, param2: int) -> dict[str, str]:
    # Task logic
    pass
```

### 3) Add error handling
- Use `self.retry()` for retries.
- Handle exceptions appropriately.
- Log errors with structured logging.

### 4) Add task to feature service (if needed)
- If feature service needs to trigger task:
  - Import task from `tasks.py`.
  - Call task with `.delay()` or `.apply_async()`.

### 5) Add tests
- Mock Celery task execution in tests.
- Test task logic (without actual Celery execution).
- Test error handling and retries.

### 6) Document task
- Document in feature `README.md`:
  - Task purpose
  - How to trigger
  - Parameters
  - Retry behavior

## Validation
- Task is defined and can be imported.
- Task can be triggered from service or API.
- Error handling works correctly.
- Tests pass.
- Documentation is complete.

## Common mistakes (avoid)
- Creating tasks outside feature `tasks.py`.
- Not handling errors in tasks.
- Not using structured logging.
- Not documenting task purpose.

## Troubleshooting
- If task doesn't execute → check Celery worker is running.
- If task fails → check logs and error handling.
- If retries don't work → verify `max_retries` and `self.retry()` usage.
