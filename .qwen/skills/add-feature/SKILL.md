---
name: add-feature
description: Implement a complete full-stack feature combining backend API and frontend UI. Use when adding a feature that requires both API endpoints and UI components working together.
---

# Add Full-Stack Feature

## When to use
- Adding a complete feature requiring both backend and frontend
- Creating a new domain module with UI and API

## Preconditions
- Feature name follows naming conventions
- Database models are identified (if needed)
- UI/UX requirements are clear

## Steps

### 1) Create backend feature
Follow `add-backend-feature` skill:
- Create structure in `backend/app/custom/features/<feature_name>/`
- Define schemas, models, service, routes
- Register router

### 2) Create frontend feature
Follow `add-frontend-feature` skill:
- Create components in `frontend/components/custom/features/<feature_name>/`
- Create pages in `frontend/app/(private)/(custom)/<feature_name>/`
- Add types and services

### 3) Connect frontend to backend
- Generate TypeScript types from OpenAPI: `npm run generate-api-types`
- Use Server Actions or API routes for communication
- Handle loading and error states

### 4) Add database migrations (if models added)
Follow `add-database-migration` skill:
- Create Alembic migration
- Apply migration
- Verify models are synchronized

### 5) Add tests
- Backend: unit tests for service, integration tests for API
- Frontend: component tests (optional)

### 6) Add documentation
- Update backend `README.md`
- Document API endpoints
- Document frontend components and pages

## Validation
- Backend API endpoints accessible and return expected responses
- Frontend pages render and interact correctly
- TypeScript types generated and used
- Database migrations applied (if models added)
- Tests pass
- No circular dependencies

## Common mistakes
- Creating backend and frontend in isolation without integration
- Not generating TypeScript types from OpenAPI
- Skipping database migrations
- Not handling loading/error states in frontend
