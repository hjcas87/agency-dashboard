# Skill — Review Feature (Enterprise Code Review)

## Goal
Review feature changes to ensure reliability, maintainability, fork-safety,
and compliance with Python 3.11+ and TypeScript standards.

## When to use
- Any PR / set of changes that adds or modifies:
  - features (backend or frontend)
  - database models
  - API endpoints
  - components or pages
  - integrations

## Review checklist (MANDATORY ORDER)

### 1) Architecture boundaries
- Client/business logic stays in `custom/features/` (backend) or `custom/` (frontend).
- `core/` changes are generic, backward-compatible, and tested.
- `shared/` contains no business rules.
- No architecture drift introduced.

---

### 2) Skills compliance
- If backend feature added → `add_backend_feature` was followed.
- If frontend feature added → `add_frontend_feature` was followed.
- If full-stack feature added → `add_feature` was followed.
- If database models changed → `add_database_migration` was followed.
- If integration added → `add_integration` was followed.
- If solution docs changed → `solution_design` was followed.

---

### 2.5) Python & Code Standards (STRICT)
The following are **non-negotiable** and violations are **Blockers**:

- Python version is **3.11+**.
- No types imported from `typing`:
  - ❌ `List`, `Dict`, `Tuple`, `Set`, `Optional`, `Union`
  - ❌ `from typing import ...`
- Use built-in generics and modern syntax:
  - ✅ `list[str]`
  - ✅ `dict[str, int]`
  - ✅ `str | None`
- All functions and methods MUST have:
  - typed inputs
  - typed return value (no implicit `Any`)
- PEP8 is strictly respected:
  - naming
  - spacing
  - import order
- No imports inside functions or methods.
  - All imports must be at module level.
- No `print` statements; structured logging only.
- Dependency changes follow the `uv` workflow:
  - `uv add` used
  - `uv.lock` updated and committed
- Database models MUST be synchronized with tables via Alembic migrations.

Violations of this section MUST be marked as Blockers.

---

### 2.6) TypeScript & Frontend Standards (STRICT)
The following are **non-negotiable** and violations are **Blockers**:

- TypeScript strict mode enabled.
- No `any` types (use `unknown` if needed).
- Server Components used by default.
- `'use client'` only when needed (interactivity, hooks, browser APIs).
- Types generated from OpenAPI schema when possible.
- Proper error handling and loading states.

Violations of this section MUST be marked as Blockers.

---

### 3) Error handling & observability
- Proper error handling in all layers (routes, services, components).
- Meaningful error messages.
- Structured logging (no prints).
- User-friendly error messages in frontend.

---

### 4) Configuration & secrets
- No secrets committed to the repository.
- Configuration is typed and documented.
- Defaults are safe and explicit.
- Environment variables used appropriately.

---

### 5) Testing
- Unit tests exist for business logic (services).
- Integration tests exist for API endpoints (if applicable).
- Component tests exist for complex UI logic (if applicable).
- Tests avoid heavy mocking when possible.

---

### 6) Database synchronization
- Models are synchronized with database tables.
- Alembic migrations created and applied.
- No manual database changes without migrations.

---

## Validation
- Reviewer can trace: request → feature → response.
- A new developer can:
  - understand the feature from code
  - run tests
  - deploy without issues
- No blockers remain unresolved.

## Output format (review comments)
- Categorize findings:
  - **Blocker**: breaks standards, fork-safety, type safety, or database synchronization
  - **Major**: maintainability, error handling, or test gaps
  - **Minor**: naming, formatting, clarity
- Provide concrete, actionable fix suggestions.
