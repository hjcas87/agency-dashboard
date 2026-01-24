# Skill — Add a new Full-Stack Feature

Tags: [feature] [fullstack] [custom]

## Goal
Implement a new full-stack feature (backend + frontend) in a fork-friendly way:
- backend feature under `backend/app/custom/features/<feature_name>/`
- frontend components under `frontend/components/custom/features/<feature_name>/`
- frontend pages under `frontend/app/(private)/(custom)/<feature_name>/`
- follows the complete feature architecture

## When to use
- Adding a complete feature that requires both backend and frontend
- Creating a new domain module with UI and API

## Preconditions
- The feature name is agreed and follows naming conventions.
- Database models are identified (if needed).
- UI/UX requirements are clear.

## Steps (MANDATORY ORDER)

### 1) Create backend feature
Follow `add_backend_feature.md`:
- Create feature structure in `backend/app/custom/features/<feature_name>/`
- Define schemas, models, service, routes
- Register router

### 2) Create frontend feature
Follow `add_frontend_feature.md`:
- Create components in `frontend/components/custom/features/<feature_name>/`
- Create pages in `frontend/app/(private)/(custom)/<feature_name>/`
- Add types and services

### 3) Connect frontend to backend
- Generate TypeScript types from OpenAPI schema: `npm run generate-api-types`
- Use Server Actions or API routes for backend communication
- Handle loading and error states

### 4) Add database migrations (if models added)
Follow `add_database_migration.md`:
- Create Alembic migration
- Apply migration
- Verify models are synchronized

### 5) Add tests
- Backend: unit tests for service, integration tests for API
- Frontend: component tests, integration tests (optional)

### 6) Add documentation
- Update backend `README.md`
- Document API endpoints
- Document frontend components and pages

## Validation
- Backend API endpoints are accessible and return expected responses.
- Frontend pages render and interact correctly.
- TypeScript types are generated and used.
- Database migrations applied (if models added).
- Tests pass (backend and frontend).
- No circular dependencies.

## Common mistakes (avoid)
- Creating backend and frontend in isolation without integration.
- Not generating TypeScript types from OpenAPI.
- Skipping database migrations.
- Not handling loading/error states in frontend.

## Troubleshooting
- If types are out of sync → regenerate from OpenAPI schema.
- If database models are out of sync → use `add_database_migration`.
- If integration issues → verify API endpoints and Server Actions.
