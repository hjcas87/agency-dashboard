---
name: add-database-migration
description: Create and apply Alembic migrations when SQLAlchemy models are modified. Use whenever database schema changes are needed. CRITICAL: models must be synchronized with database tables.
---

# Add Database Migration

## When to use
- Adding a new SQLAlchemy model
- Modifying an existing model (adding/removing columns, changing types)
- Renaming columns or tables
- Any change to database schema

## Rules (STRICT)
- **NEVER** modify models without creating a migration
- **NEVER** modify database manually without migrations
- **ALWAYS** verify models are synchronized after migration

## Steps

### 1) Modify the model
- Update SQLAlchemy model in `models.py`
- Ensure type hints are correct

### 2) Generate migration
```bash
cd backend
uv run alembic revision --autogenerate -m "Description of changes"
```

### 3) Review generated migration
- Check `backend/alembic/versions/` for the new migration file
- Review the generated SQL: column additions/deletions, data types

### 4) Edit migration if needed
- If autogenerate missed something, edit manually
- Add data migrations if needed (default values, transformations)

### 5) Apply migration
```bash
cd backend
uv run alembic upgrade head
```

### 6) Verify synchronization
- Check that model fields match database columns
- Run tests to ensure models work correctly

### 7) Commit migration
- Commit both model changes (`models.py`) and migration file

## Validation
- Migration file created and reviewed
- Migration applied successfully
- Models synchronized with database tables
- Tests pass with new schema

## Common mistakes
- Modifying models without migrations
- Not reviewing generated migrations
- Not applying migrations before committing
- Forgetting to commit migration files
