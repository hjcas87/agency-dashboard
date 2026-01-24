# Frontend Architecture & Best Practices

## Overview

This document outlines the architecture, patterns, and best practices for the frontend application. The frontend is built with **Next.js 14+ (App Router)**, **React 19**, **TypeScript**, and **Tailwind CSS**.

## Table of Contents

- [Architecture Principles](#architecture-principles)
- [Folder Structure](#folder-structure)
- [Code Organization Patterns](#code-organization-patterns)
- [Security Best Practices](#security-best-practices)
- [Performance & Scalability](#performance--scalability)
- [Testing Strategy](#testing-strategy)
- [Code Quality](#code-quality)

## Architecture Principles

### 1. **Separation of Concerns**

- **UI Components**: Pure presentational components with minimal logic
- **Custom Hooks**: Business logic and state management
- **Services**: API calls and external integrations
- **Types**: TypeScript definitions organized by feature

### 2. **Feature-Based Organization**

Organize code by features rather than by technical type:

```
app/
├── (features)/
│   ├── n8n/
│   │   ├── components/        # Feature-specific components
│   │   ├── hooks/            # Feature-specific hooks
│   │   ├── services/         # Feature-specific services
│   │   ├── types.ts          # Feature-specific types
│   │   └── page.tsx          # Feature page
│   └── users/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── types.ts
```

### 3. **Core vs Custom**

Following the backend pattern:

- **`components/core/`**: Base components (shadcn/ui, NOT modifiable)
- **`components/custom/`**: Custom components (modifiable)
- **`lib/core/`**: Core utilities and services (NOT modifiable)
- **`lib/custom/`**: Custom utilities and services (modifiable)

### 4. **Type Safety First**

- Use TypeScript strictly (no `any` unless absolutely necessary)
- Generate types from OpenAPI schema: `npm run generate-api-types`
- Define feature-specific types in `types.ts` files

### 5. **Server Components by Default**

- Use Server Components when possible (default in App Router)
- Use `'use client'` only when needed (interactivity, hooks, browser APIs)

## Folder Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Route group: Public authentication routes
│   │   ├── login/
│   │   └── reset-password/
│   ├── (private)/            # Route group: Protected private routes
│   │   ├── layout.tsx        # Core - Authentication check (NOT modifiable in forks)
│   │   ├── page.tsx          # Custom - Home dashboard (each fork can override)
│   │   └── (custom)/         # Core - Directory for client-specific custom routes
│   │       ├── .gitkeep      # Core - Keeps directory in git
│   │       └── [custom pages] # Custom - Client-specific pages (protected by layout.tsx)
│   ├── api/                  # API routes
│   │   ├── (core)/           # Core API endpoints (NOT modifiable)
│   │   │   ├── auth/         # Authentication endpoints
│   │   │   └── proxy/        # Generic proxy
│   │   └── (custom)/         # Custom API endpoints (modifiable)
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Public home page
│
├── components/              # React components
│   ├── core/               # Base components (NOT modifiable)
│   │   └── ui/             # shadcn/ui components
│   └── custom/             # Custom components (modifiable)
│       ├── features/       # Feature-specific components
│       │   └── n8n/
│       │       └── WorkflowStatus.tsx
│       ├── layouts/        # Layout components
│       └── ui/             # Custom UI components
│
├── lib/                    # Utilities and shared code
│   ├── core/              # Core utilities (NOT modifiable)
│   │   └── api/           # API client, types
│   ├── custom/            # Custom utilities (modifiable)
│   │   ├── features/      # Feature-specific services
│   │   │   └── n8n/
│   │   │       └── n8nService.ts
│   │   ├── hooks/         # Custom hooks
│   │   │   ├── usePolling.ts
│   │   │   └── useApiCall.ts
│   │   └── utils/         # Utility functions
│   └── utils.ts           # Common utilities
│
├── hooks/                  # Global custom hooks (legacy, prefer lib/custom/hooks)
├── types/                  # Global TypeScript types
│   └── global.d.ts        # Global type declarations
│
├── docs/                   # Documentation
│   └── ARCHITECTURE.md    # This file
│
├── public/                 # Static assets
├── .env.local             # Environment variables (gitignored)
├── next.config.js         # Next.js configuration
├── tailwind.config.ts     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## Route Groups and Private Routes

### Structure

The app uses Next.js route groups to organize public and private routes:

- **`(auth)/`**: Public authentication routes (login, password reset)
- **`(private)/`**: Protected private routes with authentication
  - **`layout.tsx`**: Core - Authentication check (NOT modifiable in forks)
  - **`page.tsx`**: Custom - Home dashboard (each fork can override)
  - **`(custom)/`**: Core - Directory for client-specific custom routes
    - All routes here are automatically protected by `(private)/layout.tsx`
    - Pages map directly to root routes (e.g., `(custom)/campaigns/page.tsx` → `/campaigns`)

### API Routes Structure

API routes also use route groups to organize core and custom endpoints:

- **`api/(core)/`**: Core API endpoints (NOT modifiable in forks)
  - **`auth/`**: Authentication endpoints (`/api/auth/login`, `/api/auth/logout`, etc.)
  - **`proxy/`**: Generic proxy (`/api/proxy/[...path]`)
- **`api/(custom)/`**: Custom API endpoints (modifiable per client)
  - Custom endpoints map to `/api/[endpoint]` (route group doesn't appear in URL)

**Note**: Route groups `(core)` and `(custom)` don't appear in public URLs, keeping URLs clean while organizing code internally.

### Authentication Flow

1. User accesses `/` (private route)
2. `proxy.ts` verifies cookie (core)
3. `(private)/layout.tsx` verifies authentication (core)
4. `(private)/page.tsx` or pages in `(custom)/` render (customizable)

### Customizing for a Client

**Option 1: Redirect to specific page**

```typescript
// app/(private)/page.tsx (in client fork)
import { redirect } from 'next/navigation'

export default async function PrivatePage() {
  redirect('/inbox') // or '/dashboard', etc.
}
```

**Option 2: Render custom dashboard**

```typescript
// app/(private)/page.tsx
import { getCurrentUser } from '@/app/actions/core/auth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/core/ui/card'

export default async function PrivatePage() {
  const user = await getCurrentUser()
  // Render custom dashboard
  return <DashboardContent user={user} />
}
```

### Rules

- ✅ **DO modify `(private)/page.tsx`** - It's custom, each fork can override
- ✅ **DO add pages in `(private)/(custom)/`** - All routes here are protected
- ❌ **DON'T modify `(private)/layout.tsx` in forks** - Unless adding wrapper components (like CRMLayout)
- ✅ **No `/crm/` prefix** - Pages in `(custom)/` map directly to root routes

## Code Organization Patterns

### 1. **Custom Hooks Pattern**

Extract reusable logic into custom hooks:

```typescript
// lib/custom/hooks/usePolling.ts
import { useEffect, useRef, useState } from 'react'

export function usePolling<T>(
  fetchFn: () => Promise<T>,
  interval: number = 1500,
  enabled: boolean = true
) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!enabled) return

    const poll = async () => {
      try {
        const result = await fetchFn()
        setData(result)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Polling error'))
      }
    }

    poll() // Poll immediately
    intervalRef.current = setInterval(poll, interval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [fetchFn, interval, enabled])

  return { data, error }
}
```

### 2. **Service Layer Pattern**

Separate API calls into services:

```typescript
// lib/custom/features/n8n/n8nService.ts
import { apiClient } from '@/lib/core/api/client'
import type { N8NTriggerRequest, N8NTriggerResponse, TaskStatusResponse } from './types'

export class N8NService {
  async triggerWorkflow(request: N8NTriggerRequest): Promise<N8NTriggerResponse> {
    const response = await fetch('/api/v1/n8n/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || error.message || 'Failed to trigger workflow')
    }

    return response.json()
  }

  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    const response = await fetch(`/api/v1/n8n/task/${taskId}`)
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || error.message || 'Failed to get task status')
    }

    return response.json()
  }
}
```

### 3. **Feature Hook Pattern**

Combine hooks and services for features:

```typescript
// lib/custom/features/n8n/useN8NWorkflow.ts
import { useState, useCallback } from 'react'
import { usePolling } from '@/lib/custom/hooks/usePolling'
import { N8NService } from './n8nService'
import type { N8NTriggerRequest, TaskStatusResponse } from './types'

export function useN8NWorkflow() {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const service = new N8NService()

  const { data: taskStatus } = usePolling<TaskStatusResponse>(
    () => service.getTaskStatus(taskId!),
    1500,
    taskId !== null && taskStatus?.state !== 'SUCCESS' && taskStatus?.state !== 'FAILURE'
  )

  const triggerWorkflow = useCallback(async (request: N8NTriggerRequest) => {
    try {
      setError(null)
      const response = await service.triggerWorkflow(request)
      setTaskId(response.task_id)
      return response
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to trigger workflow')
      setError(error)
      throw error
    }
  }, [service])

  return {
    triggerWorkflow,
    taskStatus,
    taskId,
    error,
  }
}
```

### 4. **Component Composition Pattern**

Keep components small and focused:

```typescript
// components/custom/features/n8n/WorkflowStatus.tsx
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/core/ui/card'
import type { TaskStatusResponse } from '@/lib/custom/features/n8n/types'

interface WorkflowStatusProps {
  status: TaskStatusResponse
}

export function WorkflowStatus({ status }: WorkflowStatusProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Estado del Workflow</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Status display logic */}
      </CardContent>
    </Card>
  )
}
```

### 5. **Type Organization Pattern**

Define types per feature:

```typescript
// lib/custom/features/n8n/types.ts
export interface N8NTriggerRequest {
  webhook_path: string
  payload?: Record<string, unknown>
}

export interface N8NTriggerResponse {
  task_id: string
  status: string
  message?: string
}

export interface TaskStatusResponse {
  task_id: string
  state: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY' | 'REVOKED'
  result?: Record<string, unknown>
  error?: string
  status?: string
}
```

## Security Best Practices

### 1. **Environment Variables**

- **Never** expose secrets in client-side code
- Use `NEXT_PUBLIC_` prefix only for public variables
- Store sensitive data server-side (API routes, Server Components)

```typescript
// ✅ Good
const apiUrl = process.env.NEXT_PUBLIC_API_URL

// ❌ Bad - Secrets in client code
const apiKey = process.env.API_KEY // This will be undefined in client
```

### 2. **Input Validation**

- Validate all user inputs
- Use Zod or similar for runtime validation
- Sanitize data before sending to API

```typescript
import { z } from 'zod'

const WorkflowRequestSchema = z.object({
  webhook_path: z.string().min(1).max(255),
  payload: z.record(z.unknown()).optional(),
})

type WorkflowRequest = z.infer<typeof WorkflowRequestSchema>
```

### 3. **API Security**

- Always validate API responses
- Handle errors gracefully
- Use HTTPS in production
- Implement request timeouts
- Sanitize error messages (don't expose internals)

### 4. **XSS Prevention**

- Use React's built-in XSS protection
- Never use `dangerouslySetInnerHTML` without sanitization
- Escape user-generated content

### 5. **CSRF Protection**

- Next.js provides CSRF protection by default
- Use SameSite cookies
- Implement CSRF tokens for sensitive operations (if needed)

## Performance & Scalability

### 1. **Code Splitting**

- Use dynamic imports for large components
- Leverage Next.js automatic code splitting

```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>,
  ssr: false, // Only if component can't be SSR'd
})
```

### 2. **Image Optimization**

- Use Next.js `Image` component
- Optimize images (WebP, AVIF)
- Use appropriate sizes

```typescript
import Image from 'next/image'

<Image
  src="/image.jpg"
  alt="Description"
  width={500}
  height={300}
  priority // For above-the-fold images
/>
```

### 3. **Memoization**

- Use `useMemo` for expensive computations
- Use `useCallback` for stable function references
- Use `React.memo` for expensive components (sparingly)

### 4. **State Management**

- Use React state for local UI state
- Consider Zustand/Redux only when needed (shared state across features)
- Prefer server state management (React Query, SWR) for API data

### 5. **Bundle Size**

- Monitor bundle size
- Use dynamic imports for large libraries
- Tree-shake unused code
- Analyze bundle: `npm run build -- --analyze`

## Testing Strategy

### 1. **Unit Tests**

- Test utilities, hooks, and services
- Use Vitest or Jest
- Target: >80% coverage

```typescript
// __tests__/lib/custom/hooks/usePolling.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { usePolling } from '@/lib/custom/hooks/usePolling'

describe('usePolling', () => {
  it('should poll at interval', async () => {
    const fetchFn = vi.fn().mockResolvedValue({ data: 'test' })
    
    renderHook(() => usePolling(fetchFn, 100))
    
    await waitFor(() => {
      expect(fetchFn).toHaveBeenCalledTimes(2) // Immediate + first interval
    })
  })
})
```

### 2. **Component Tests**

- Test component behavior, not implementation
- Use React Testing Library

### 3. **E2E Tests**

- Test critical user flows
- Use Playwright or Cypress
- Run in CI/CD

## Code Quality

### 1. **Linting & Formatting**

- ESLint for code quality
- Prettier for formatting
- Run before commit: `npm run lint && npm run format:check`

### 2. **Type Safety**

- Strict TypeScript mode
- No `any` types (use `unknown` if needed)
- Use type guards for runtime checks

### 3. **Naming Conventions**

- **Components**: PascalCase (`WorkflowStatus`)
- **Functions/Variables**: camelCase (`triggerWorkflow`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- **Types/Interfaces**: PascalCase (`TaskStatusResponse`)
- **Files**: 
  - Components: PascalCase (`WorkflowStatus.tsx`)
  - Utilities: camelCase (`usePolling.ts`)
  - Types: camelCase (`types.ts`)

### 4. **Code Organization Rules**

- One component per file
- One hook per file
- Co-locate related files (feature-based)
- Keep files small (<300 lines ideally)

### 5. **Documentation**

- Document complex logic
- Use JSDoc for public APIs
- Keep README files updated
- Document architectural decisions

## Migration Guide

When refactoring existing code:

1. **Identify feature boundaries**
2. **Extract services** from components
3. **Create custom hooks** for reusable logic
4. **Move types** to feature-specific files
5. **Create feature components** from page components
6. **Test incrementally**

## Examples

See the `examples/` directory for:
- Feature implementation examples
- Hook usage patterns
- Service layer examples
- Component composition examples

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [shadcn/ui](https://ui.shadcn.com/)

