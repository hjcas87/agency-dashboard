# Migración de Autenticación a Core

## Resumen

La funcionalidad de autenticación (login, usuarios, JWT, SSR) ha sido movida de `custom/` a `core/` porque es una funcionalidad base del boilerplate que todos los proyectos necesitarán.

## Cambios Realizados

### Backend

✅ **Ya estaba en core**: `backend/app/core/features/auth/`
- `models.py` - UserPassword, PasswordResetToken
- `schemas.py` - LoginRequest, LoginResponse, etc.
- `service.py` - AuthService con login, logout, password reset
- `routes.py` - Endpoints `/api/v1/auth/*`
- `dependencies.py` - get_current_user, get_current_active_user
- `utils.py` - JWT, bcrypt, password hashing

### Frontend

✅ **Movido a core**:

1. **Componentes**:
   - `frontend/components/custom/features/auth/` → `frontend/components/core/features/auth/`
   - `LoginForm.tsx` - Formulario de login con Server Action
   - `AuthGuard.tsx` - Guard del cliente (para casos especiales)
   - `ServerAuthGuard.tsx` - Guard del servidor (recomendado)

2. **Hooks y Utilidades**:
   - `frontend/lib/custom/features/auth/` → `frontend/lib/core/features/auth/`
   - `useAuth.ts` - Hook para estado de autenticación

3. **Server Actions**:
   - `frontend/app/actions/auth.ts` → `frontend/app/actions/core/auth.ts`
   - `loginAction()` - Login con httpOnly cookies
   - `logoutAction()` - Logout
   - `getCurrentUser()` - Obtener usuario actual

## Referencias Actualizadas

Todas las referencias han sido actualizadas:

- ✅ `app/login/page.tsx` → `@/components/core/features/auth/LoginForm`
- ✅ `app/crm/layout.tsx` → `@/components/core/features/auth/ServerAuthGuard`
- ✅ `app/page.tsx` → `@/app/actions/core/auth`
- ✅ `components/core/features/auth/*` → `@/app/actions/core/auth`
- ✅ `components/custom/features/crm/Layout.tsx` → `@/lib/core/features/auth/useAuth`

## Estructura Final

```
backend/app/
├── core/features/
│   ├── auth/          ✅ Autenticación (JWT, bcrypt, passwords)
│   └── users/         ✅ Usuarios básicos (CRUD)
│
└── custom/features/
    └── crm/           ✅ Features específicos del cliente

frontend/
├── components/core/features/
│   └── auth/          ✅ Componentes de autenticación
│
├── lib/core/features/
│   └── auth/          ✅ Hooks y utilidades
│
├── app/actions/core/
│   └── auth.ts        ✅ Server Actions
│
└── components/custom/features/
    └── crm/           ✅ Features específicos del cliente
```

## Próximos Pasos

### Para Merge a Main

1. **Verificar que todo funciona**:
   ```bash
   # Backend
   cd backend
   uv run pytest
   
   # Frontend
   cd frontend
   npm run build
   ```

2. **Crear PR a main**:
   - Todos los cambios de autenticación deben ir a `main`
   - La branch `crm-prego` solo debe tener features específicos del CRM

3. **Documentar en main**:
   - Actualizar `docs/ARCHITECTURE.md` con autenticación
   - Actualizar `README.md` con instrucciones de autenticación
   - Documentar Server Actions y SSR

## Funcionalidades Core de Autenticación

### Backend

- ✅ Login con email/password
- ✅ JWT tokens con expiración
- ✅ Password hashing con bcrypt
- ✅ Password reset con tokens
- ✅ Password change (requiere autenticación)
- ✅ Crear usuarios con password (admin only)
- ✅ Protección de rutas con `get_current_user`

### Frontend

- ✅ Página de login con Server Action
- ✅ Server-Side Rendering (SSR)
- ✅ httpOnly cookies para tokens
- ✅ Server Auth Guard
- ✅ Client Auth Guard (para casos especiales)
- ✅ Hook `useAuth` para estado de autenticación
- ✅ API routes de Next.js como proxy seguro

## Notas Importantes

1. **No modificar core**: Una vez en `main`, `core/features/auth/` no debe modificarse en branches de clientes
2. **Extender en custom**: Si un cliente necesita funcionalidad adicional, debe extenderse en `custom/`
3. **SSR por defecto**: Priorizar Server Components y Server Actions
4. **Seguridad**: Tokens siempre en httpOnly cookies, nunca en localStorage

## Testing

Antes de merge a main, verificar:

- [ ] Login funciona correctamente
- [ ] Logout elimina cookies
- [ ] Rutas protegidas requieren autenticación
- [ ] Password reset funciona
- [ ] Server Actions funcionan
- [ ] SSR renderiza correctamente
- [ ] Cookies httpOnly se configuran correctamente

