---
name: add-frontend-feature
description: Implement a new frontend UI feature using Next.js App Router, Server Components, and custom components directory. Use when adding UI pages, client-specific components, or extending frontend functionality.
---

# Add Frontend Feature

## When to use
- Adding a new UI feature or page
- Creating client-specific components
- Extending frontend functionality

## Preconditions
- Feature name follows kebab-case for routes, PascalCase for components
- API endpoints are identified (if backend integration needed)

## Steps

### 1) Create component directory
```
frontend/components/custom/features/<feature_name>/
├── <FeatureName>.tsx
├── types.ts           # TypeScript types (if needed)
├── hooks/             # Custom hooks (if needed)
└── services/          # API calls (if needed)
```

### 2) Create page (if needed)
```
frontend/app/(private)/(custom)/<feature_name>/page.tsx
```
- Use Server Components by default
- Add `'use client'` only if interactivity is needed

### 3) Define types
- Create `types.ts` if feature-specific types are needed
- Use types generated from OpenAPI schema when possible
- Avoid `any` types

### 4) Implement components
- Start with Server Components
- Use `'use client'` only for: interactive elements, browser APIs, React hooks
- Follow shadcn/ui patterns for UI components

### 5) Add API integration (if needed)
- Create service functions in `services/` or use Server Actions
- Use Server Actions for mutations (`app/actions/custom/`)
- Use API routes for complex logic (`app/api/(custom)/`)

### 6) Add error handling
- Handle loading states
- Handle error states
- Provide user feedback

### 7) Add tests (if applicable)
- Component tests for UI logic

### 8) Update navigation (if needed)
- Add links to navigation components

## Validation
- Components render without errors
- Pages are accessible at expected routes
- TypeScript compiles without errors
- No `any` types
- Server Components used by default

## Common mistakes
- Using `'use client'` unnecessarily
- Putting business logic in components (use services or Server Actions)
- Using `any` types
- Creating components in `components/core/` instead of `components/custom/`
- Not handling loading/error states
