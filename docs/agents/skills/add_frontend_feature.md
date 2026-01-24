# Skill — Add a new Frontend Feature

Tags: [frontend] [feature] [custom]

## Goal
Implement a new frontend feature in a fork-friendly way:
- components live under `frontend/components/custom/features/<feature_name>/`
- pages live under `frontend/app/(private)/(custom)/<feature_name>/`
- it uses Server Components by default
- it follows Next.js App Router conventions

## When to use
- Adding a new UI feature or page
- Creating client-specific components
- Extending frontend functionality

## Preconditions
- The feature name is agreed and follows naming conventions (kebab-case for routes, PascalCase for components).
- API endpoints are identified (if backend integration needed).

## Steps (MANDATORY ORDER)

### 1) Create component directory
Create:
`frontend/components/custom/features/<feature_name>/`
- Component files (`.tsx`)
- `types.ts` (TypeScript types, if needed)
- `hooks/` (custom hooks, if needed)
- `services/` (API calls, if needed)

### 2) Create page (if needed)
Create:
`frontend/app/(private)/(custom)/<feature_name>/page.tsx`
- Use Server Components by default.
- Add `'use client'` only if interactivity is needed.

### 3) Define types
- Create `types.ts` if feature-specific types are needed.
- Use types generated from OpenAPI schema when possible.
- Avoid `any` types.

### 4) Implement components
- Start with Server Components.
- Use `'use client'` only for:
  - Interactive elements (buttons, forms)
  - Browser APIs (localStorage, etc.)
  - React hooks (useState, useEffect, etc.)
- Follow shadcn/ui patterns for UI components.

### 5) Add API integration (if needed)
- Create service functions in `services/` or use Server Actions.
- Use Server Actions for mutations (`app/actions/custom/`).
- Use API routes for complex logic (`app/api/(custom)/`).

### 6) Add error handling
- Handle loading states.
- Handle error states.
- Provide user feedback.

### 7) Add tests (if applicable)
- Component tests for UI logic.
- Integration tests for user flows (optional).

### 8) Update navigation (if needed)
- Add links to navigation components.
- Update routing if needed.

## Validation
- Components render without errors.
- Pages are accessible at expected routes.
- TypeScript compiles without errors.
- No `any` types (use `unknown` if needed).
- Server Components are used by default.
- Client Components are only used when necessary.

## Common mistakes (avoid)
- Using `'use client'` unnecessarily (use Server Components by default).
- Putting business logic in components (use services or Server Actions).
- Using `any` types.
- Creating components in `components/core/` instead of `components/custom/`.
- Not handling loading/error states.

## Troubleshooting
- If API integration needed → create Server Actions or API routes.
- If complex state management needed → use React hooks or state management library.
- If types are missing → generate from OpenAPI schema or define in `types.ts`.
