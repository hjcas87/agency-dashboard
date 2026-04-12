# Frontend Documentation

Welcome to the Frontend documentation. This directory contains the Next.js 14+ (App Router) application built with React 19, TypeScript, and Tailwind CSS.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Format code
npm run format
npm run format:check

# Generate API types from FastAPI OpenAPI schema
npm run generate-api-types
```

## Architecture Overview

This frontend follows a **feature-based architecture** with clear separation of concerns:

- **Components**: UI components (presentational)
- **Hooks**: Business logic and state management
- **Services**: API calls and external integrations
- **Types**: TypeScript definitions organized by feature

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed architecture documentation.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router (pages/routes)
├── components/            # React components
│   ├── core/             # Base components (shadcn/ui, NOT modifiable)
│   └── custom/           # Custom components (modifiable)
├── lib/                  # Utilities and shared code
│   ├── core/            # Core utilities (NOT modifiable)
│   └── custom/          # Custom utilities (modifiable)
│       ├── features/    # Feature-specific code
│       ├── hooks/       # Custom hooks
│       └── utils/       # Utility functions
├── docs/                # Documentation
├── public/              # Static assets
└── types/               # Global TypeScript types
```

## Key Features

- ✅ **Type-Safe API Client**: Generated from FastAPI OpenAPI schema
- ✅ **Feature-Based Organization**: Code organized by feature, not by type
- ✅ **Custom Hooks**: Reusable business logic (polling, API calls, etc.)
- ✅ **Service Layer**: Clean separation of API calls
- ✅ **Component Composition**: Small, focused, reusable components
- ✅ **TypeScript**: Strict type checking
- ✅ **Tailwind CSS**: Utility-first styling with shadcn/ui

## Best Practices

See [docs/BEST_PRACTICES.md](./docs/BEST_PRACTICES.md) for comprehensive best practices covering:

- Code organization
- Component patterns
- State management
- API integration
- Error handling
- Performance optimization
- Security guidelines
- Testing patterns

## Core vs Custom

Following the backend pattern, the codebase is divided into:

- **`core/`**: Base components and utilities (NOT modifiable in forks)
- **`custom/`**: Custom components and utilities (modifiable)

This allows the boilerplate to be updated while preserving customizations.

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## Development Workflow

1. **Create a new feature**:
   - Create feature directory in `lib/custom/features/`
   - Add types in `types.ts`
   - Create service in `service.ts` (if needed)
   - Create hook in `useFeatureName.ts` (if needed)
   - Create components in `components/custom/features/feature-name/`
   - Create page in `app/(features)/feature-name/page.tsx`

2. **Add a new hook**:
   - Create file in `lib/custom/hooks/`
   - Export from hook file
   - Document with JSDoc

3. **Add a new component**:
   - Create file in `components/custom/`
   - Use shadcn/ui components from `components/core/ui/`
   - Keep components small and focused

## Code Style

- **TypeScript**: Strict mode, no `any` unless absolutely necessary
- **Formatting**: Prettier (configured)
- **Linting**: ESLint with Next.js config
- **Naming**:
  - Components: PascalCase
  - Functions/Variables: camelCase
  - Constants: UPPER_SNAKE_CASE
  - Types: PascalCase

## Testing

```bash
# Run tests (when configured)
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

See [docs/BEST_PRACTICES.md](./docs/BEST_PRACTICES.md#testing-patterns) for testing patterns.

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)

## Getting Help

- Review [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for architecture details
- Review [docs/BEST_PRACTICES.md](./docs/BEST_PRACTICES.md) for coding guidelines
- Check existing code in `lib/custom/features/` for examples
