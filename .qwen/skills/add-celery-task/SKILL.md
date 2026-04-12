---
name: add-celery-task
description: Add a Celery background task within a feature. Use when adding long-running operations, async processing, or scheduled background tasks.
---

# Add Celery Background Task

## When to use
- Adding long-running operations
- Adding async processing
- Adding scheduled tasks

## Preconditions
- Feature exists under `custom/features/<feature_name>/`
- Task requirements are understood

## Steps

### 1) Create tasks.py in feature
```
backend/app/custom/features/<feature_name>/tasks.py
```
- Import `celery_app` from `app.core.tasks.celery_app`

### 2) Define task
```python
from app.core.tasks.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def my_task(self, param1: str, param2: int) -> dict[str, str]:
    pass
```

### 3) Add error handling
- Use `self.retry()` for retries
- Handle exceptions appropriately
- Log errors with structured logging

### 4) Add task to feature service (if needed)
- Import task from `tasks.py`
- Call task with `.delay()` or `.apply_async()`

### 5) Add tests
- Mock Celery task execution in tests
- Test task logic and error handling

### 6) Document task
- Document in feature `README.md`: purpose, trigger method, parameters, retry behavior

## Validation
- Task is defined and can be imported
- Task can be triggered from service or API
- Error handling works correctly
- Tests pass

## Common mistakes
- Creating tasks outside feature `tasks.py`
- Not handling errors in tasks
- Not using structured logging
- Not documenting task purpose
