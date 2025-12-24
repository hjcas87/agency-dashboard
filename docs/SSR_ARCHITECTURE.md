# Arquitectura Server-Side Rendering (SSR)

## Principio: Priorizar SSR por Seguridad

Siempre que sea posible, usamos **Server Components** y **Server Actions** en lugar de Client Components para:

1. ✅ **Mayor Seguridad**: El código se ejecuta en el servidor, no se expone al cliente
2. ✅ **Mejor Performance**: Menos JavaScript enviado al cliente
3. ✅ **Mejor SEO**: Contenido renderizado en el servidor
4. ✅ **Acceso a Cookies httpOnly**: Solo accesibles desde el servidor

## Arquitectura Actual

### Server Components (Por Defecto)

Los componentes en Next.js 13+ son **Server Components por defecto**. Solo agregamos `"use client"` cuando es necesario.

#### Cuándo usar Server Components:
- ✅ Páginas que solo muestran datos
- ✅ Layouts y componentes de estructura
- ✅ Componentes que no necesitan interactividad
- ✅ Componentes que acceden a cookies/datos del servidor

#### Cuándo usar Client Components (`"use client"`):
- ✅ Componentes con interactividad (onClick, onChange, etc.)
- ✅ Componentes que usan hooks de React (useState, useEffect, etc.)
- ✅ Componentes que usan contextos del cliente
- ✅ Componentes de UI interactivos (formularios, modales, etc.)

## Implementación

### 1. Server Actions

Las **Server Actions** son funciones que se ejecutan en el servidor y pueden ser llamadas desde Client Components.

**Ubicación**: `frontend/app/actions/`

```typescript
// app/actions/auth.ts
"use server"

export async function loginAction(formData: FormData) {
  // Código ejecutado en el servidor
  // Acceso seguro a cookies httpOnly
  // Llamadas a FastAPI
}
```

**Ventajas**:
- ✅ Ejecución en el servidor (más seguro)
- ✅ Acceso a cookies httpOnly
- ✅ No expone lógica al cliente
- ✅ Mejor performance

### 2. Server Components para Páginas

```typescript
// app/crm/page.tsx (Server Component)
import { getDashboardData } from "../actions/crm"

export default async function CRMPage() {
  // Datos obtenidos en el servidor
  const data = await getDashboardData()
  
  // Renderizado en el servidor
  return <DashboardMain initialData={data} />
}
```

### 3. Client Components para Interactividad

```typescript
// components/custom/features/crm/DashboardMain.tsx
"use client"

export function DashboardMain({ initialData }: Props) {
  // Componente interactivo que recibe datos del servidor
  // Puede usar hooks, eventos, etc.
}
```

## Flujo de Datos

```
1. Usuario → Página (Server Component)
2. Server Component → Server Action
3. Server Action → FastAPI (con token de cookie httpOnly)
4. FastAPI → Datos
5. Server Component → Renderiza con datos
6. Cliente → Recibe HTML renderizado
```

## Ejemplos Implementados

### ✅ Autenticación

**Antes** (Client Component):
```typescript
"use client"
const handleSubmit = async () => {
  const response = await fetch("/api/auth/login", {...})
  // Token expuesto en JavaScript
}
```

**Ahora** (Server Action):
```typescript
"use server"
export async function loginAction(formData: FormData) {
  // Token guardado en cookie httpOnly en el servidor
  // Nunca expuesto al cliente
}
```

### ✅ Protección de Rutas

**Antes** (Client Component):
```typescript
"use client"
export function AuthGuard({ children }) {
  const { isAuthenticated } = useAuth() // Verificación en cliente
  // ...
}
```

**Ahora** (Server Component):
```typescript
export async function ServerAuthGuard({ children }) {
  const user = await getCurrentUser() // Verificación en servidor
  if (!user) redirect("/login")
  return <>{children}</>
}
```

### ✅ Dashboard

**Antes** (Client Component):
```typescript
"use client"
useEffect(() => {
  fetch("/api/proxy/dashboards") // Petición desde cliente
}, [])
```

**Ahora** (Server Component + Server Action):
```typescript
// page.tsx (Server Component)
export default async function CRMPage() {
  const data = await getDashboardData() // Server Action
  return <DashboardMain initialData={data} />
}
```

## Mejores Prácticas

### 1. Minimizar Client Components

- ✅ Usar Server Components por defecto
- ✅ Agregar `"use client"` solo cuando sea necesario
- ✅ Separar lógica del servidor de la del cliente

### 2. Server Actions para Mutaciones

- ✅ Usar Server Actions para formularios
- ✅ Usar Server Actions para operaciones que requieren autenticación
- ✅ Mantener lógica sensible en el servidor

### 3. Datos Iniciales

- ✅ Obtener datos en Server Components
- ✅ Pasar datos como props a Client Components
- ✅ Evitar fetch en useEffect cuando sea posible

### 4. Cookies httpOnly

- ✅ Solo accesibles desde Server Components/Actions
- ✅ Nunca expuestas al cliente
- ✅ Más seguras que localStorage

## Estructura de Archivos

```
frontend/
├── app/
│   ├── actions/          # Server Actions
│   │   ├── auth.ts       # Acciones de autenticación
│   │   └── crm.ts        # Acciones del CRM
│   ├── api/              # API Routes (cuando sea necesario)
│   │   └── auth/
│   ├── crm/
│   │   ├── page.tsx      # Server Component
│   │   └── layout.tsx    # Server Component
│   └── login/
│       └── page.tsx       # Server Component
└── components/
    └── custom/
        └── features/
            └── auth/
                ├── LoginForm.tsx        # Client Component (interactivo)
                └── ServerAuthGuard.tsx  # Server Component
```

## Ventajas de SSR

### Seguridad
- ✅ Código no expuesto al cliente
- ✅ Cookies httpOnly accesibles
- ✅ Validación en el servidor
- ✅ Menos superficie de ataque

### Performance
- ✅ Menos JavaScript enviado
- ✅ Renderizado inicial más rápido
- ✅ Mejor First Contentful Paint (FCP)
- ✅ Mejor Time to Interactive (TTI)

### SEO
- ✅ Contenido renderizado en servidor
- ✅ Mejor indexación
- ✅ Mejor para crawlers

## Conclusión

Priorizamos **Server-Side Rendering** siempre que sea posible para maximizar la seguridad y performance. Solo usamos Client Components cuando es absolutamente necesario para interactividad.

