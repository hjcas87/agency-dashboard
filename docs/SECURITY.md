# Seguridad del Sistema de Autenticación

## Arquitectura de Seguridad Mejorada

### ✅ Nueva Arquitectura (Más Segura)

```
Frontend (React) → API Routes Next.js (/api/*) → FastAPI Backend
                    ↓
              httpOnly Cookies
              (Token nunca expuesto al cliente)
```

**Ventajas:**
1. ✅ **Token en httpOnly cookie**: No accesible desde JavaScript (protección XSS)
2. ✅ **API Routes como proxy**: El token nunca se expone al cliente
3. ✅ **Validación en servidor**: Todas las peticiones pasan por Next.js primero

### Comparación con Django

| Aspecto | Django | Nuestro Sistema | Estado |
|---------|--------|-----------------|--------|
| **Hash de Contraseñas** | PBKDF2 (default) | bcrypt | ✅ Similar seguridad |
| **Salt** | Automático | Automático (bcrypt) | ✅ Incluido |
| **Algoritmo** | PBKDF2SHA256 | bcrypt | ✅ Ambos seguros |
| **Tokens** | Sesiones (cookies) | JWT (httpOnly cookies) | ✅ Más moderno |
| **Protección XSS** | Cookies httpOnly | Cookies httpOnly | ✅ Protegido |
| **Expiración** | Configurable | 30 min (configurable) | ✅ Incluido |
| **Verificación** | `check_password()` | `bcrypt.checkpw()` | ✅ Similar |

### Bcrypt vs PBKDF2

- **Bcrypt**: Algoritmo diseñado específicamente para contraseñas, resistente a ataques de fuerza bruta
- **PBKDF2**: Algoritmo de derivación de clave, también seguro
- **Conclusión**: Ambos son seguros para producción. Bcrypt es más común en aplicaciones modernas.

## Implementación Actual

### Backend (FastAPI)

1. **Hash de Contraseñas**:
   ```python
   # Usa bcrypt directamente (mismo nivel que Django)
   salt = bcrypt.gensalt()  # Salt automático
   hashed = bcrypt.hashpw(password_bytes, salt)
   ```

2. **Verificación**:
   ```python
   # Verifica de forma segura sin exponer la contraseña
   bcrypt.checkpw(password_bytes, hashed_password_bytes)
   ```

3. **JWT Tokens**:
   - Firmados con `SECRET_KEY`
   - Expiración configurable (30 min por defecto)
   - Algoritmo: HS256

4. **Protección de Rutas**:
   - Dependency `get_current_user` valida el token
   - Verifica expiración automáticamente
   - Valida que el usuario esté activo

### Frontend (Next.js)

#### API Routes (Intermediario Seguro)

1. **`/api/auth/login`**:
   - ✅ Recibe credenciales del cliente
   - ✅ Llama a FastAPI `/api/v1/auth/login`
   - ✅ Guarda token en **httpOnly cookie**
   - ✅ Retorna usuario (sin token)

2. **`/api/auth/logout`**:
   - ✅ Elimina cookie httpOnly
   - ✅ Limpia sesión

3. **`/api/auth/me`**:
   - ✅ Verifica token desde cookie
   - ✅ Obtiene usuario de FastAPI
   - ✅ Retorna información del usuario

4. **`/api/proxy/[...path]`**:
   - ✅ Proxy para todas las peticiones a FastAPI
   - ✅ Lee token de cookie httpOnly
   - ✅ Envía token a FastAPI en header Authorization
   - ✅ Retorna respuesta al cliente

#### Cliente (React)

1. **Login**:
   - ✅ Llama a `/api/auth/login` (Next.js API route)
   - ✅ No maneja tokens directamente
   - ✅ Token se guarda automáticamente en cookie httpOnly

2. **Peticiones API**:
   - ✅ Usa `apiClient` que apunta a `/api/proxy`
   - ✅ Cookies se envían automáticamente (credentials: 'include')
   - ✅ Token nunca se expone al JavaScript del cliente

3. **Protección de Rutas**:
   - ✅ `AuthGuard` verifica autenticación con `/api/auth/me`
   - ✅ Redirige a `/login` si no está autenticado
   - ✅ Hook `useAuth` para estado de autenticación

## Flujo de Autenticación Completo

```
1. Usuario → /login (Next.js)
2. Next.js Client → POST /api/auth/login (Next.js API Route)
3. Next.js API Route → POST /api/v1/auth/login (FastAPI)
4. FastAPI → Verifica email/password con bcrypt
5. FastAPI → Genera JWT token
6. FastAPI → Retorna { access_token, user }
7. Next.js API Route → Guarda token en httpOnly cookie
8. Next.js API Route → Retorna { user } (sin token)
9. Next.js Client → Redirige a /crm
10. Next.js Client → Peticiones a /api/proxy/contacts
11. Next.js API Route → Lee token de cookie httpOnly
12. Next.js API Route → Envía token a FastAPI
13. FastAPI → Valida token y retorna datos
```

## Seguridad de Cookies

### Configuración de Cookies httpOnly

```typescript
cookieStore.set("access_token", token, {
  httpOnly: true,        // No accesible desde JavaScript
  secure: true,          // Solo HTTPS en producción
  sameSite: "lax",       // Protección CSRF
  maxAge: 30 * 60,        // 30 minutos
  path: "/",              // Disponible en todo el sitio
})
```

### Ventajas de httpOnly Cookies

1. ✅ **Protección XSS**: JavaScript no puede acceder al token
2. ✅ **Automático**: Se envía en cada petición
3. ✅ **Seguro**: Solo accesible desde el servidor
4. ✅ **CSRF Protection**: Con `sameSite: "lax"`

## Estado Actual de la Implementación

### ✅ Backend (FastAPI)

1. **Autenticación JWT**:
   - ✅ Tokens firmados con `SECRET_KEY`
   - ✅ Expiración: 30 minutos (configurable)
   - ✅ Algoritmo: HS256

2. **Hash de Contraseñas**:
   - ✅ Bcrypt con salt automático
   - ✅ Límite de 72 bytes manejado correctamente
   - ✅ Verificación segura sin exponer contraseñas

3. **Protección de Rutas**:
   - ✅ **TODAS las rutas del CRM están protegidas** con `get_current_user`
   - ✅ Rutas protegidas: `/contacts`, `/leads`, `/opportunities`, `/activities`, `/pipelines`, `/automations`, `/integrations`, `/dashboards`
   - ✅ Validación de token en cada petición
   - ✅ Verificación de usuario activo

4. **Endpoints de Autenticación**:
   - ✅ `POST /api/v1/auth/login` - Login
   - ✅ `GET /api/v1/auth/me` - Obtener usuario actual
   - ✅ `POST /api/v1/auth/logout` - Logout
   - ✅ `POST /api/v1/auth/reset-password` - Solicitar reset
   - ✅ `POST /api/v1/auth/change-password` - Cambiar contraseña (requiere token)
   - ✅ `POST /api/v1/auth/create-user` - Crear usuario (solo admin)

### ✅ Frontend (Next.js)

1. **API Routes (Intermediario)**:
   - ✅ `/api/auth/login` - Login con httpOnly cookie
   - ✅ `/api/auth/logout` - Logout
   - ✅ `/api/auth/me` - Verificar autenticación
   - ✅ `/api/proxy/[...path]` - Proxy para FastAPI

2. **Cliente (React)**:
   - ✅ Página `/login` conectada con API routes
   - ✅ Token nunca expuesto al cliente
   - ✅ Cookies se envían automáticamente
   - ✅ Protección de rutas con `AuthGuard`

## Mejoras de Seguridad Recomendadas

### Para Producción

1. **HTTPS Obligatorio**:
   - ✅ Configurar SSL/TLS en producción
   - ✅ Nunca enviar tokens por HTTP
   - ✅ Cookies `secure: true` solo en HTTPS

2. **Refresh Tokens** (Opcional):
   - Implementar refresh tokens para renovar sin re-login
   - Tokens de corta duración (15 min) + refresh tokens largos

3. **Rate Limiting**:
   - Limitar intentos de login (ej: 5 intentos por minuto)
   - Prevenir ataques de fuerza bruta
   - Implementar en Next.js API routes

4. **CORS Configurado**:
   - ✅ Ya configurado en `config.py`
   - Solo permitir dominios autorizados

5. **Headers de Seguridad**:
   - Agregar headers como `X-Content-Type-Options`, `X-Frame-Options`
   - Implementar en Next.js middleware

6. **CSRF Protection**:
   - ✅ `sameSite: "lax"` en cookies
   - Considerar tokens CSRF adicionales si es necesario

## Conclusión

✅ **El sistema es SEGURO y equivalente a Django** en términos de seguridad de contraseñas.

✅ **La integración está COMPLETA y MEJORADA**: 
   - Next.js API Routes como intermediario seguro
   - Token en httpOnly cookie (no expuesto al cliente)
   - Todas las rutas del CRM están protegidas

✅ **Más seguro que localStorage**: 
   - Protección contra XSS
   - Token nunca accesible desde JavaScript
   - Cookies httpOnly con configuración segura

✅ **Listo para producción** con las mejoras recomendadas (HTTPS, rate limiting, etc.).
