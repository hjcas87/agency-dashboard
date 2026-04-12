---
name: review-feature
description: Perform enterprise code review checking architecture boundaries, type safety, coding standards, and fork-safety. Use when reviewing PRs, changes, or acting as quality gate.
---

# Review Feature (Enterprise Code Review)

## When to use
- Any PR / set of changes that adds or modifies features, models, API endpoints, components, or integrations

## Review Checklist

### 1) Architecture boundaries
- Client/business logic stays in `custom/features/` (backend) or `custom/` (frontend)
- `core/` changes are generic, backward-compatible, and tested
- `shared/` contains no business rules

### 2) Python Standards (STRICT — Blockers)
- Python 3.11+ with built-in generics: `list[str]`, `dict[str, int]`, `str | None`
- NO imports from `typing` for `List`, `Dict`, `Optional`, `Union`
- All functions have typed inputs and return values
- No imports inside functions (module-level only)
- No `print` statements (structured logging only)
- `uv` workflow: `uv add`, `uv lock` updated and committed
- Database models synchronized via Alembic migrations

### 3) TypeScript Standards (STRICT — Blockers)
- TypeScript strict mode
- No `any` types (use `unknown` if needed)
- Server Components by default
- `'use client'` only when needed (interactivity, hooks, browser APIs)
- Proper error handling and loading states

### 4) Error handling & observability
- Proper error handling in all layers
- Meaningful error messages, structured logging
- User-friendly error messages in frontend

### 5) Configuration & secrets
- No secrets committed to repository
- Configuration is typed and documented
- Environment variables used appropriately

### 6) Testing
- Unit tests exist for business logic
- Integration tests exist for API endpoints
- Tests avoid heavy mocking

### 7) Database synchronization
- Models synchronized with database tables
- Alembic migrations created and applied

## Output format
Categorize findings:
- **Blocker**: breaks standards, fork-safety, type safety, database sync
- **Major**: maintainability, error handling, test gaps
- **Minor**: naming, formatting, clarity

Provide concrete, actionable fix suggestions.
