# Cursor Rules - Core Project Rules

> **IMPORTANT**: Always respond to the user in Spanish in chat conversations, even though this documentation is in English.

## Language Guidelines

- **Solution Design Documents** (`docs/solution_design/`): MUST be in Spanish (for client review)
- **Code and Comments**: MUST be in English (standard practice)
- **Technical Documentation** (READMEs, ARCHITECTURE.md, AGENTS.md): MUST be in English
- **Chat Responses**: MUST be in Spanish (user communication)

## Project Context

This is a reusable boilerplate for Forward Deployed Engineers with modular feature-based architecture.

## Architecture

- **Frontend**: Next.js 14+ with shadcn/ui and Tailwind CSS
- **Backend**: FastAPI with feature-based architecture (core/custom)
- **Message Broker**: Kafka for robust asynchronous messaging
- **Automation**: N8N self-hosted with webhooks
- **Background Tasks**: Celery for asynchronous tasks

## Directory Structure

```
backend/app/
├── core/features/     # Core features (DO NOT modify in forks)
├── custom/features/   # Custom features (modify here)
└── shared/           # Shared code (interfaces, services, repos)
```

## Fundamental Principles

1. **Never modify code in `core/`** - All customizations go in `custom/`
2. **Changes in `core/` go to `main` first** - Then update working branch from `main`
3. **Feature-Based Architecture** - Each feature is self-contained
4. **Separation of Concerns** - Routes → Service → Repository → Model
5. **Dependency Injection** - Use FastAPI dependencies
6. **Interfaces and Abstractions** - Use interfaces from `shared/interfaces/`
7. **Testing** - Follow TDD, maintain > 80% coverage
8. **Database Model Synchronization** - SQLAlchemy models MUST be synchronized with database tables. There MUST NOT be differences between fields defined in models and columns in tables. Use Alembic migrations to maintain synchronization.

## Code Conventions

### Python (Backend)

- **Formatting**: Black with line-length=100
- **Imports**: isort with profile=black
- **Linting**: Ruff (replaces flake8)
- **Type hints**: Always use type hints when possible
  - **IMPORTANT**: Python 3.11+ - Use built-in types, DO NOT import from typing:
    - `list[T]` instead of `List[T]`
    - `dict[K, V]` instead of `Dict[K, V]`
    - `tuple[T, ...]` instead of `Tuple[T, ...]`
    - `T | None` instead of `Optional[T]`
    - Only import from `typing` when necessary (e.g., `Any`, `Callable`, `TypeVar`, `Generic`)
- **Docstrings**: Google style for public functions
- **Naming**:
  - Classes: PascalCase
  - Functions/variables: snake_case
  - Constants: UPPER_SNAKE_CASE

### TypeScript/React (Frontend)

- **Formatting**: Prettier (configured in project)
- **Imports**: Order imports correctly
- **Naming**:
  - Components: PascalCase
  - Functions/variables: camelCase
  - Constants: UPPER_SNAKE_CASE

## Design Patterns

1. **Repository Pattern** - For data access
2. **Service Layer** - For business logic
3. **Dependency Injection** - FastAPI dependencies
4. **Interface Segregation** - Specific interfaces in `shared/interfaces/`
5. **Wrapper Pattern** - For external services (N8N, Kafka)

## Feature Structure

Each feature must have:

```
feature_name/
├── routes.py      # FastAPI endpoints
├── schemas.py    # Pydantic schemas
├── service.py    # Business logic
├── repository.py # Data access (optional)
├── models.py     # SQLAlchemy models (optional)
├── tasks.py      # Celery tasks (optional, if background tasks are needed)
└── README.md     # Documentation
```

### Celery Tasks

**Celery tasks must be self-contained within each feature:**

- Each feature that needs background tasks must have its own `tasks.py`
- Location: `backend/app/core/features/<feature>/tasks.py` or `backend/app/custom/features/<feature>/tasks.py`
- Celery will discover them automatically with `autodiscover_tasks`
- **NEVER** create centralized task modules - each feature manages its own tasks

## Testing

- **Unit Tests**: Fast tests without external dependencies
- **Integration Tests**: Tests with DB and mocked services
- **E2E Tests**: End-to-end tests with all services
- **Coverage**: Maintain > 80%
- **Naming**: `test_<what>_<condition>_<expected_result>`

## Dependency Management

- **Backend**: Use `uv` for package management
- **Configuration**: Everything in `pyproject.toml`
- **Lock file**: Generate `uv.lock` for deterministic builds

## Important Commands

```bash
# Development
make dev              # Start services
make test             # Run tests
make lint             # Check formatting
make format           # Format code

# Backend
uv pip install -e ".[dev]"  # Install dependencies
uv run pytest                # Run tests
uv run black app             # Format code
```

## Specific Rules

### When creating a new feature:

1. Create complete structure in `custom/features/`
2. Implement routes, schemas, service
3. If background tasks are needed, create `tasks.py` within the feature
4. Add tests (unit + integration)
5. Register router in `custom/features/__init__.py`
6. Document in feature README

### When modifying code:

1. **Never** modify `core/` - Only `custom/`
2. Use interfaces from `shared/interfaces/` when possible
3. Follow existing patterns in core features
4. Add tests for changes
5. Maintain coverage > 80%

### When modifying SQLAlchemy models:

1. **ALWAYS** create an Alembic migration for model changes
2. **NEVER** modify models without updating the database through migrations
3. **ALWAYS** verify that model fields match table columns
4. **ALWAYS** run migrations after modifying them: `alembic upgrade head`
5. If there are discrepancies, fix them immediately through migrations or adjusting the model
6. Models and database must always be synchronized - this is a critical rule

### When using external services:

1. Create wrapper implementing interface from `shared/interfaces/`
2. Use dependency injection
3. Mock in tests
4. Document in README

## Documentation

- Keep READMEs updated
- Document architectural decisions
- Add usage examples
- Document APIs with docstrings

## Business Documentation

**IMPORTANT**: Before implementing any feature, ALWAYS consult:

1. **`docs/business/requirements/`** - Functional requirements and user stories
2. **`docs/business/diagrams/`** - Flow diagrams, architecture, sequence
3. **`docs/business/designs/`** - UI/UX designs (Figma, mockups, wireframes)
4. **`docs/business/specs/`** - Business technical specifications

### How to Use Business Documentation

- **Diagrams**: Reference diagrams when implementing business flows
- **Figma/PDF Designs**: Follow specified components, styles, and layouts
- **Images**: Use as visual reference for implementation
- **Requirements**: Verify that implementation meets all requirements

### When Implementing a Feature

1. **Review business documentation** in `docs/business/`
2. **Consult relevant diagrams** to understand flows
3. **Follow UI/UX designs** provided
4. **Meet business and API specifications**
5. **Document deviations** if any

### Reference Documentation

When implementing code, include comments referencing documentation:

```python
# Implementation according to docs/business/requirements/checkout.md
# Flow: docs/business/diagrams/flowcharts/checkout-flow.png
# Design: docs/business/designs/figma/checkout.figma
def process_checkout(order_data: OrderCreate) -> Order:
    # ...
```

## Common Mistakes to Avoid

1. ❌ Modifying code in `core/`
2. ❌ Creating circular dependencies
3. ❌ Ignoring tests
4. ❌ Hardcoding values (use config)
5. ❌ Coupling features together
6. ❌ Not using type hints
7. ❌ Not documenting public code
8. ❌ **Modifying SQLAlchemy models without creating migrations** - CRITICAL
9. ❌ **Having differences between models and database tables** - CRITICAL
10. ❌ Modifying database manually without creating migrations
11. ❌ **Using ServerAuthGuard in protected layouts** - CRITICAL (causes infinite loops, middleware already handles protection)
12. ❌ **Modifying cookies in Server Components** - Only allowed in Server Actions or Route Handlers
13. ❌ **Validating token in middleware** - Middleware should only verify cookie existence, not token validity
14. ❌ **Redirecting from middleware when cookie exists in /login** - Causes loops if token is invalid, let login page handle this

## Git Workflow: Core vs Custom

**CRITICAL**: When modifying code in `core/`, you must follow this flow:

### Core Changes (MANDATORY: use `dev` branch)

**ALL core development MUST be done in the `dev` branch first.**

1. **Work in `dev` branch**:
   - Switch to `dev`: `git checkout dev`
   - Create feature branch if needed: `git checkout -b feat/my-feature`
   - Make changes to `core/` code
   - Commit to `dev` (or feature branch, then merge to `dev`)

2. **Review and analysis**:
   - Developer in charge reviews changes in `dev`
   - Code review, testing, and analysis happens in `dev`
   - Fixes are made in `dev`

3. **Merge to `main`** (only after approval):
   - Once reviewed and approved: `git checkout main && git merge dev`
   - `main` is the stable branch for core code

4. **Update client branches**:
   - After `dev` → `main` merge, update client branches: `git checkout <client-branch> && git merge main`
   - `.gitattributes` automatically resolves conflicts

**NEVER commit core changes directly to `main`**. They must go through `dev` first.

### Custom Changes (client branches)

- Commit directly to client branch (`crm-prego`, `crm-artistealo`, etc.)
- No need to go through `dev` or `main`
- Client branches are independent for custom development

### Future: Client Forks

When creating actual forks for clients (instead of branches):
- Each fork will have its own `main` and `dev` branches
- Same workflow applies: `dev` → `main` for core changes in the fork

See `AGENTS.md` for detailed process with commands.

## Documentation References

- `AGENTS.md` - Complete guide for AI agents
- `ARCHITECTURE.md` - Project architecture
- `docs/PROJECT_BRIEF.template.md` - Template to create client PROJECT_BRIEF
- `docs/solution_design/` - Solution documentation agreed with client
- `docs/agents/roles/` - Agent roles
- `docs/agents/skills/` - Agent skills/procedures

## When the Agent Works

- **Always** verify that changes are in `custom/` if it's custom code
- **Always** follow existing feature structure
- **Always** add tests for new functionality
- **Always** use type hints
- **Always** verify that code follows conventions
- **Always** consult `docs/business/` before implementing features
- **Always** reference diagrams and designs when implementing
- **Always** follow correct git flow when modifying `core/` code
- **Always** keep SQLAlchemy models synchronized with database
- **Always** create Alembic migrations when modifying models
- **Never** modify `core/` without explicit reason
- **Never** commit `core/` changes in custom branch without passing to `main` first
- **Never** create circular dependencies
- **Never** hardcode configuration values
- **Never** implement without reviewing relevant business documentation
- **Never** modify models without creating corresponding migrations
- **Never** leave discrepancies between models and database tables
- **Never** use ServerAuthGuard in protected layouts (middleware already handles protection)
- **Never** validate token in middleware (only verify cookie existence)
