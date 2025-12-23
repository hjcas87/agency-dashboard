# React 19 Migration Guide

Esta guía documenta los cambios necesarios al migrar de React 18 a React 19.

## Versiones Actualizadas

- **React**: `18.2.0` → `19.2.3`
- **React-DOM**: `18.2.0` → `19.2.3`
- **Next.js**: `14.0.4` → `15.5.9`
- **@types/react**: `^18.3.12` → `^19.0.0`
- **@types/react-dom**: `^18.3.1` → `^19.0.0`

## Cambios Principales en React 19

### 1. Nuevas Características

#### Actions (Server Actions mejoradas)
React 19 mejora el soporte para Server Actions en Next.js.

#### use() Hook
Nuevo hook para manejar promesas y contextos de forma más eficiente.

#### useOptimistic Hook
Hook para actualizaciones optimistas de UI.

### 2. Cambios en TypeScript

Los tipos de React 19 tienen algunos cambios:

```typescript
// React 18
import { FC } from 'react'

// React 19 - FC sigue disponible pero se recomienda usar function components directamente
function MyComponent() {
  return <div>Hello</div>
}
```

### 3. Cambios en refs

Las refs ahora pueden ser funciones o objetos:

```typescript
// Ambas formas funcionan
const ref1 = useRef<HTMLDivElement>(null)
const ref2 = (node: HTMLDivElement | null) => { /* ... */ }
```

### 4. Cambios en Context

El API de Context sigue siendo compatible, pero hay mejoras internas.

## Cambios en Next.js 15

### 1. App Router (Estable)

Next.js 15 consolida el App Router como la forma principal de desarrollo.

### 2. Server Components por Defecto

Los componentes son Server Components por defecto. Usar `'use client'` cuando se necesite interactividad.

### 3. Nuevas APIs

- Mejor soporte para Server Actions
- Mejoras en streaming y suspenso
- Optimizaciones de rendimiento

## Verificación Post-Migración

### 1. Instalar Dependencias

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 2. Verificar Build

```bash
npm run build
```

### 3. Ejecutar Tests

```bash
npm run type-check
npm run lint
```

### 4. Probar Aplicación

```bash
npm run dev
```

## Posibles Problemas y Soluciones

### Error: "Cannot find module 'react'"

**Solución**: Reinstalar dependencias
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error: TypeScript types incompatibles

**Solución**: Actualizar tipos
```bash
npm install --save-dev @types/react@^19.0.0 @types/react-dom@^19.0.0
```

### Warning: "use client" directive

**Solución**: Agregar `'use client'` al inicio de componentes que usan hooks del cliente:
```typescript
'use client'

import { useState } from 'react'

export function MyComponent() {
  const [state, setState] = useState(0)
  // ...
}
```

### Error: Server Component usando hooks del cliente

**Solución**: Mover el componente a un Client Component o extraer la lógica del cliente.

## Recursos

- [React 19 Release Notes](https://react.dev/blog/2024/12/05/react-19)
- [Next.js 15 Release Notes](https://nextjs.org/blog/next-15)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/12/05/react-19-upgrade-guide)
- [Next.js Migration Guide](https://nextjs.org/docs/app/building-your-application/upgrading/version-15)

