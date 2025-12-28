# Flujo de Autenticación

Este documento describe el flujo de autenticación implementado en el proyecto y las mejores prácticas para mantenerlo funcionando correctamente.

## Arquitectura de Autenticación

El sistema de autenticación utiliza un enfoque de **doble capa**:

1. **Middleware** (`frontend/middleware.ts`): Verifica la existencia de cookies antes de que la request llegue a la página
2. **Validación en componentes**: La validación del token se hace cuando los componentes necesitan datos del usuario

## Flujo de Login

```
Usuario hace login
  ↓
loginAction establece cookie httpOnly
  ↓
redirect("/crm")
  ↓
Middleware verifica cookie en /crm
  ↓
Si hay cookie → permite acceso
Si no hay cookie → redirect("/login")
  ↓
Página /crm se renderiza
  ↓
Componentes hacen llamadas al backend con el token
```

## Componentes Principales

### 1. Middleware (`frontend/middleware.ts`)

El middleware verifica la existencia de la cookie `access_token` antes de que la request llegue a las páginas:

```typescript
// Si la ruta es /crm o sus subrutas, verificar que haya cookie
if (pathname.startsWith('/crm')) {
  const token = request.cookies.get('access_token')
  
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}
```

**IMPORTANTE**: El middleware solo verifica la **existencia** de la cookie, no su validez. La validación del token se hace en los componentes cuando se necesitan datos del usuario.

### 2. Server Actions (`frontend/app/actions/core/auth.ts`)

#### `loginAction`

- Establece la cookie `access_token` con configuración segura:
  - `httpOnly: true` - Previene acceso desde JavaScript (protección XSS)
  - `secure: true` (en producción) - Solo HTTPS (protección sniffing)
  - `sameSite: "lax"` - Balance seguridad/funcionalidad (recomendado OWASP)
  - `path: "/"` - Cookie disponible en toda la aplicación
- Usa `revalidatePath("/", "layout")` para asegurar que la cookie esté disponible
- Redirige a `/crm` usando `redirect()`

#### `getCurrentUser`

- Lee el token desde la cookie
- Valida el token llamando al backend (`/api/v1/auth/me`)
- Retorna el usuario si el token es válido, `null` si no lo es

### 3. Página de Login (`frontend/app/(auth)/login/page.tsx`)

- Verifica si el usuario ya está autenticado usando `getCurrentUser()`
- Si está autenticado, redirige a `/crm`
- Si no está autenticado, muestra el formulario de login

## ⚠️ Reglas Críticas

### 1. NO usar ServerAuthGuard en layouts protegidos

**PROHIBIDO**:
```typescript
// ❌ NO HACER ESTO
export default async function CRMRootLayout({ children }) {
  return (
    <ServerAuthGuard>
      {children}
    </ServerAuthGuard>
  )
}
```

**Por qué**: `ServerAuthGuard` causa problemas de timing cuando se ejecuta inmediatamente después de establecer la cookie. El middleware ya maneja la protección básica, y la validación del token se hace en los componentes cuando se necesitan datos.

**CORRECTO**:
```typescript
// ✅ CORRECTO - Solo middleware
export default async function CRMRootLayout({ children }) {
  return <>{children}</>
}
```

El middleware ya verifica la cookie antes de que la request llegue aquí.

### 2. Middleware solo verifica existencia de cookie

El middleware NO debe validar el token llamando al backend porque:
- Es demasiado lento (cada request)
- Causa problemas de timing
- El middleware debe ser rápido y simple

### 3. Validación del token en componentes

La validación del token se hace cuando los componentes necesitan datos del usuario:

```typescript
// ✅ CORRECTO - Validar cuando se necesitan datos
export default async function DashboardPage() {
  const user = await getCurrentUser()
  
  if (!user) {
    // El middleware ya debería haber redirigido, pero por si acaso:
    redirect("/login")
  }
  
  // Usar datos del usuario
  return <Dashboard user={user} />
}
```

### 4. Cookies solo en Server Actions

Las cookies solo pueden modificarse en:
- Server Actions (`"use server"`)
- Route Handlers (`app/api/**/route.ts`)

**PROHIBIDO**:
```typescript
// ❌ NO HACER ESTO en Server Components
export default async function SomeComponent() {
  const cookieStore = await cookies()
  cookieStore.set("token", "value") // ❌ Error!
}
```

### 5. revalidatePath después de establecer cookie

Siempre llamar `revalidatePath("/", "layout")` después de establecer una cookie antes de hacer `redirect()`:

```typescript
cookieStore.set("access_token", token, { ... })
revalidatePath("/", "layout")
redirect("/crm")
```

## Flujo de Errores

### Token inválido

Si un token es inválido:
1. `getCurrentUser()` retorna `null`
2. Los componentes que necesitan datos del usuario pueden redirigir a `/login`
3. El usuario puede hacer login de nuevo, lo que establecerá una nueva cookie válida

### Cookie expirada

1. El middleware no encuentra la cookie
2. Redirige a `/login`
3. El usuario puede hacer login de nuevo

## Seguridad de Cookies

### Configuración Recomendada

```typescript
cookieStore.set("access_token", token, {
  httpOnly: true,        // ✅ Previene XSS
  secure: process.env.NODE_ENV === "production", // ✅ Solo HTTPS en producción
  sameSite: "lax",      // ✅ Balance seguridad/funcionalidad (recomendado OWASP)
  maxAge: 30 * 60,      // ✅ Expiración (30 minutos o 30 días si "recordarme")
  path: "/",            // ✅ Disponible en toda la aplicación
})
```

### ¿Por qué `sameSite: "lax"`?

- **`strict`**: Más seguro pero rompe redirects desde emails/links externos
- **`lax`**: Permite redirects GET cross-site pero bloquea POST/forms (protección CSRF) - Recomendado por OWASP
- **`none`**: Menos seguro, requiere `secure: true`

## Testing

Al probar la autenticación:

1. Verificar que el login establece la cookie correctamente
2. Verificar que el middleware redirige a `/login` si no hay cookie
3. Verificar que `/crm` se renderiza correctamente cuando hay cookie válida
4. Verificar que los componentes manejan correctamente cuando `getCurrentUser()` retorna `null`

## Troubleshooting

### Problema: Loop infinito entre /crm y /login

**Causa**: `ServerAuthGuard` en el layout está causando problemas de timing.

**Solución**: Eliminar `ServerAuthGuard` del layout. El middleware ya maneja la protección.

### Problema: Cookie no disponible después de login

**Causa**: No se está llamando `revalidatePath()` después de establecer la cookie.

**Solución**: Siempre llamar `revalidatePath("/", "layout")` después de `cookieStore.set()` y antes de `redirect()`.

### Problema: Redirect a /login después de login exitoso

**Causa**: `ServerAuthGuard` está validando el token antes de que la cookie esté disponible.

**Solución**: Eliminar `ServerAuthGuard` del layout. El middleware ya verifica la cookie.

## Referencias

- [Next.js Cookies Documentation](https://nextjs.org/docs/app/api-reference/functions/cookies)
- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [OWASP Cookie Security](https://owasp.org/www-community/HttpOnly)
