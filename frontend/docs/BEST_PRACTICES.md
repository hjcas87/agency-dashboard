# Frontend Best Practices

This document provides practical guidelines and examples for writing maintainable, scalable, and secure frontend code.

## Table of Contents

- [Code Organization](#code-organization)
- [Component Patterns](#component-patterns)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)
- [Security Guidelines](#security-guidelines)
- [Testing Patterns](#testing-patterns)

## Code Organization

### File Naming Conventions

```
✅ Good:
- WorkflowStatus.tsx          (Component)
- useN8NWorkflow.ts          (Hook)
- n8nService.ts              (Service)
- taskStateUtils.ts          (Utility)
- types.ts                   (Types)

❌ Bad:
- workflow-status.tsx
- useN8NWorkflow.tsx
- N8NService.ts
- utils.ts (too generic)
```

### Import Organization

```typescript
// 1. React and Next.js
import { useState, useEffect } from 'react'
import Image from 'next/image'

// 2. Third-party libraries
import { z } from 'zod'

// 3. Internal - Core components
import { Button } from '@/components/core/ui/button'

// 4. Internal - Custom components
import { WorkflowStatus } from '@/components/custom/features/n8n/WorkflowStatus'

// 5. Internal - Hooks
import { useN8NWorkflow } from '@/lib/custom/features/n8n/useN8NWorkflow'

// 6. Internal - Services
import { N8NService } from '@/lib/custom/features/n8n/n8nService'

// 7. Internal - Utils
import { getTaskStateLabel } from '@/lib/custom/utils/taskStateUtils'

// 8. Internal - Types
import type { TaskStatusResponse } from '@/lib/custom/features/n8n/types'

// 9. Relative imports
import './styles.css'
```

## Component Patterns

### 1. Keep Components Small and Focused

```typescript
// ✅ Good: Single responsibility
export function WorkflowStatus({ status }: WorkflowStatusProps) {
  return <Card>...</Card>
}

// ❌ Bad: Too many responsibilities
export function WorkflowManager() {
  // Handles API calls, state, UI, polling, etc.
}
```

### 2. Extract Logic to Custom Hooks

```typescript
// ✅ Good: Logic separated from UI
export function WorkflowPage() {
  const { triggerWorkflow, taskStatus, error } = useN8NWorkflow()

  return (
    <div>
      <Button onClick={() => triggerWorkflow({ webhook_path: '...' })}>
        Trigger
      </Button>
      {taskStatus && <WorkflowStatus status={taskStatus} />}
    </div>
  )
}

// ❌ Bad: Logic mixed with UI
export function WorkflowPage() {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Complex polling logic here...
  }, [])

  const handleClick = async () => {
    // API call logic here...
  }

  return <div>...</div>
}
```

### 3. Use TypeScript Strictly

```typescript
// ✅ Good: Explicit types
interface WorkflowStatusProps {
  status: TaskStatusResponse
  onReset?: () => void
}

export function WorkflowStatus({ status, onReset }: WorkflowStatusProps) {
  // ...
}

// ❌ Bad: Using any
export function WorkflowStatus({ status, onReset }: any) {
  // ...
}
```

### 4. Destructure Props

```typescript
// ✅ Good
export function Button({ children, onClick, disabled }: ButtonProps) {
  // ...
}

// ❌ Bad
export function Button(props: ButtonProps) {
  return <button onClick={props.onClick}>{props.children}</button>
}
```

## State Management

### 1. Use Local State for UI State

```typescript
// ✅ Good: UI state stays local
export function SearchInput() {
  const [query, setQuery] = useState('')
  // ...
}

// ❌ Bad: Lifting state unnecessarily
export function SearchInput({ query, setQuery }: Props) {
  // ...
}
```

### 2. Use Custom Hooks for Complex State

```typescript
// ✅ Good: Complex state logic in hook
function useN8NWorkflow() {
  const [taskId, setTaskId] = useState<string | null>(null)
  const { data: taskStatus } = usePolling(...)
  // Complex logic here
  return { triggerWorkflow, taskStatus, error }
}

// ❌ Bad: Complex state logic in component
function WorkflowPage() {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState(null)
  // 50 lines of state management logic...
}
```

### 3. Avoid Prop Drilling

```typescript
// ✅ Good: Use context or composition
function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Routes />
      </ThemeProvider>
    </AuthProvider>
  )
}

// ❌ Bad: Prop drilling
function App({ user, theme }) {
  return <Routes user={user} theme={theme} />
}
function Routes({ user, theme }) {
  return <Page user={user} theme={theme} />
}
```

## API Integration

### 1. Use Service Layer

```typescript
// ✅ Good: Service encapsulates API logic
export class N8NService {
  async triggerWorkflow(request: N8NTriggerRequest): Promise<N8NTriggerResponse> {
    const response = await fetch('/api/v1/n8n/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error('Failed to trigger workflow')
    }

    return response.json()
  }
}

// ❌ Bad: API calls directly in components
function Component() {
  const handleClick = async () => {
    const response = await fetch('/api/v1/n8n/trigger', {
      method: 'POST',
      // ...
    })
    // ...
  }
}
```

### 2. Handle Errors Gracefully

```typescript
// ✅ Good: Proper error handling
try {
  const result = await service.triggerWorkflow(request)
  // Handle success
} catch (error) {
  if (error instanceof Error) {
    // Show user-friendly error message
    setError(error.message)
  } else {
    setError('An unexpected error occurred')
  }
}

// ❌ Bad: No error handling
const result = await service.triggerWorkflow(request) // Might throw
```

### 3. Use Type-Safe API Clients

```typescript
// ✅ Good: Type-safe API calls
import { apiClient } from '@/lib/core/api/client'

const { data, error } = await apiClient.GET('/api/v1/users/{id}', {
  params: { path: { id: '123' } },
})

// ❌ Bad: Unchecked API calls
const response = await fetch(`/api/v1/users/${id}`)
const data = await response.json() // No type safety
```

## Error Handling

### 1. User-Friendly Error Messages

```typescript
// ✅ Good: User-friendly messages
catch (error) {
  if (error instanceof NetworkError) {
    setError('No se pudo conectar al servidor. Verifica tu conexión.')
  } else if (error instanceof ValidationError) {
    setError('Por favor, verifica los datos ingresados.')
  } else {
    setError('Ocurrió un error inesperado. Por favor, intenta nuevamente.')
  }
}

// ❌ Bad: Technical error messages
catch (error) {
  setError(error.toString()) // "TypeError: Cannot read property..."
}
```

### 2. Error Boundaries

```typescript
// ✅ Good: Catch component errors
'use client'

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallback={<ErrorFallback />}
      onError={(error) => {
        // Log to error tracking service
        console.error('Component error:', error)
      }}
    >
      {children}
    </ErrorBoundary>
  )
}
```

### 3. Loading States

```typescript
// ✅ Good: Show loading state
const { data, error, isLoading } = useQuery(...)

if (isLoading) return <LoadingSpinner />
if (error) return <ErrorMessage error={error} />
return <DataDisplay data={data} />

// ❌ Bad: No loading state
const { data } = useQuery(...)
return <DataDisplay data={data} /> // data might be undefined
```

## Performance Optimization

### 1. Memoization (Use Sparingly)

```typescript
// ✅ Good: Memoize expensive computations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data)
}, [data])

// ❌ Bad: Memoize everything (premature optimization)
const simpleValue = useMemo(() => data.id, [data])
```

### 2. Code Splitting

```typescript
// ✅ Good: Lazy load heavy components
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
  ssr: false,
})

// ❌ Bad: Import everything upfront
import HeavyComponent from './HeavyComponent'
```

### 3. Image Optimization

```typescript
// ✅ Good: Use Next.js Image component
import Image from 'next/image'

<Image
  src="/image.jpg"
  alt="Description"
  width={500}
  height={300}
  priority={isAboveFold}
/>

// ❌ Bad: Regular img tag
<img src="/image.jpg" alt="Description" />
```

## Security Guidelines

### 1. Never Trust Client Input

```typescript
// ✅ Good: Validate on server
// Client sends request
const response = await fetch('/api/users', {
  method: 'POST',
  body: JSON.stringify({ email, password }),
})

// Server validates
// ❌ Bad: Trust client validation
// Client: "I promise this email is valid"
if (email.includes('@')) {
  // Trusted! (DON'T DO THIS)
}
```

### 2. Sanitize User Content

```typescript
// ✅ Good: Use React's built-in escaping
<div>{userInput}</div> // Automatically escaped

// ❌ Bad: dangerouslySetInnerHTML without sanitization
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

### 3. Secure Environment Variables

```typescript
// ✅ Good: Only public vars in NEXT_PUBLIC_
const apiUrl = process.env.NEXT_PUBLIC_API_URL

// Server-side only (API routes)
const secretKey = process.env.SECRET_KEY // ✅ Not exposed to client

// ❌ Bad: Secrets in client code
const apiKey = process.env.API_KEY // ❌ Will be undefined in client
```

### 4. HTTPS in Production

```typescript
// ✅ Good: Always use HTTPS in production
const apiUrl =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === 'production' ? 'https://api.example.com' : 'http://localhost:8000')
```

## Testing Patterns

### 1. Test Behavior, Not Implementation

```typescript
// ✅ Good: Test what user sees
test('shows error message when API fails', async () => {
  mockApi.mockReject(new Error('API Error'))
  render(<Component />)
  await userEvent.click(screen.getByText('Submit'))
  expect(screen.getByText(/error/i)).toBeInTheDocument()
})

// ❌ Bad: Test implementation details
test('calls setError when API fails', () => {
  const setError = jest.fn()
  // Testing internal state management
})
```

### 2. Test Hooks in Isolation

```typescript
// ✅ Good: Test hook separately
test('usePolling stops when condition is met', async () => {
  const { result } = renderHook(() =>
    usePolling(fetchFn, {
      stopCondition: data => data?.complete === true,
    })
  )
  // ...
})
```

### 3. Mock External Dependencies

```typescript
// ✅ Good: Mock services
jest.mock('@/lib/custom/features/n8n/n8nService')

test('triggers workflow', async () => {
  const mockTrigger = jest.fn().mockResolvedValue({ task_id: '123' })
  N8NService.prototype.triggerWorkflow = mockTrigger

  render(<Component />)
  await userEvent.click(screen.getByText('Trigger'))

  expect(mockTrigger).toHaveBeenCalled()
})
```

## Common Anti-Patterns to Avoid

### 1. ❌ Don't Use `any`

```typescript
// ❌ Bad
function process(data: any) {
  return data.value
}

// ✅ Good
function process<T extends { value: unknown }>(data: T) {
  return data.value
}
```

### 2. ❌ Don't Mix Concerns

```typescript
// ❌ Bad: Component does everything
function Component() {
  // API call
  // State management
  // Business logic
  // UI rendering
  // Error handling
}

// ✅ Good: Separate concerns
function Component() {
  const { data, error } = useFeatureHook()
  return <FeatureUI data={data} error={error} />
}
```

### 3. ❌ Don't Create Deep Nesting

```typescript
// ❌ Bad: Deep nesting
<div>
  <div>
    <div>
      <div>
        <Component />
      </div>
    </div>
  </div>
</div>

// ✅ Good: Flatten structure
<Container>
  <Content>
    <Component />
  </Content>
</Container>
```

### 4. ❌ Don't Ignore TypeScript Errors

```typescript
// ❌ Bad: Suppress errors
// @ts-ignore
const value = problematicCode()

// ✅ Good: Fix the root cause
const value = properlyTypedCode()
```

## Code Review Checklist

Before submitting code for review, ensure:

- [ ] Components are small and focused
- [ ] Logic is extracted to hooks/services
- [ ] TypeScript types are properly defined
- [ ] Error handling is implemented
- [ ] Loading states are shown
- [ ] Code is properly formatted (Prettier)
- [ ] No linting errors
- [ ] No `any` types (unless absolutely necessary)
- [ ] Environment variables are properly used
- [ ] User input is validated
- [ ] Error messages are user-friendly
- [ ] Performance considerations are addressed
- [ ] Accessibility is considered (if applicable)

## Resources

- [React Best Practices](https://react.dev/learn)
- [Next.js Best Practices](https://nextjs.org/docs)
- [TypeScript Best Practices](https://www.typescriptlang.org/docs/)
- [Web Security Guidelines](https://owasp.org/www-project-web-security-testing-guide/)
