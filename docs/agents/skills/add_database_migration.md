# Skill — Add Database Migration

Tags: [database] [migration] [alembic]

## Goal
Create and apply Alembic migrations when SQLAlchemy models are modified.

**CRITICAL**: Models MUST be synchronized with database tables. This skill ensures that synchronization.

## When to use
- Adding a new SQLAlchemy model.
- Modifying an existing model (adding/removing columns, changing types).
- Renaming columns or tables.
- Any change to database schema.

## Rules (STRICT)
- **NEVER** modify models without creating a migration.
- **NEVER** modify database manually without migrations.
- **ALWAYS** verify models are synchronized after migration.

## Steps (MANDATORY ORDER)

### 1) Modify the model
- Update SQLAlchemy model in `models.py`.
- Ensure type hints are correct.
- Add/remove fields as needed.

### 2) Generate migration
```bash
cd backend
uv run alembic revision --autogenerate -m "Description of changes"
```

### 3) Review generated migration
- Check `backend/alembic/versions/` for the new migration file.
- Review the generated SQL:
  - Verify column additions/deletions are correct.
  - Verify data types are correct.
  - Check for any unexpected changes.

### 4) Edit migration if needed
- If autogenerate missed something, edit the migration file manually.
- Add data migrations if needed (e.g., default values, transformations).

### 5) Apply migration
```bash
cd backend
uv run alembic upgrade head
```

### 6) Verify synchronization
- Check that model fields match database columns.
- Run tests to ensure models work correctly.
- Verify no errors in application logs.

### 7) Commit migration
- Commit both:
  - Model changes (`models.py`)
  - Migration file (`alembic/versions/...`)

## Validation
- Migration file created and reviewed.
- Migration applied successfully (`alembic upgrade head`).
- Models are synchronized with database tables.
- Tests pass with new schema.
- No errors in application.

## Common mistakes (avoid)
- Modifying models without migrations.
- Modifying database manually without migrations.
- Not reviewing generated migrations.
- Not applying migrations before committing.
- Forgetting to commit migration files.

## Troubleshooting
- If migration fails → check database state, rollback if needed.
- If models are out of sync → create migration to fix discrepancies.
- If autogenerate misses changes → edit migration manually.
