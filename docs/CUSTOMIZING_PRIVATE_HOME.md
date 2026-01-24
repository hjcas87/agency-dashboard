# Personalizar la Página Home Privada por Cliente

## Estrategia

La estructura estándar `app/(private)/` permite que cada fork/cliente personalice su página home privada (`/`) sin modificar `main` ni romper el fork.

## Arquitectura

```
app/(private)/
├── layout.tsx      # Core - Verifica autenticación (NO modificar en forks)
├── page.tsx        # Core - Importa DefaultPage (NO modificar en forks)
└── default.tsx     # Custom - Cada fork puede sobrescribir este archivo
```

### Flujo

1. Usuario accede a `/` (ruta privada)
2. `proxy.ts` verifica cookie (core)
3. `(private)/layout.tsx` verifica autenticación (core)
4. `(private)/page.tsx` renderiza `DefaultPage` (core)
5. `(private)/default.tsx` muestra contenido o redirige (customizable por fork)

## Cómo Personalizar para un Nuevo Cliente

### Opción 1: Redirigir a una Página Específica

```typescript
// app/(private)/default.tsx (en la rama custom del cliente)
import { redirect } from 'next/navigation'

/**
 * Página principal por defecto para [Cliente] CRM.
 * Redirige a la página principal del CRM.
 */
export default async function DefaultPage() {
  redirect('/dashboard') // o '/inbox', '/crm', etc.
}
```

### Opción 2: Renderizar un Dashboard Personalizado

```typescript
// app/(private)/default.tsx (en la rama custom del cliente)
import { getCurrentUser } from '@/app/actions/core/auth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/core/ui/card'

/**
 * Dashboard principal por defecto para [Cliente] CRM.
 */
export default async function DefaultPage() {
  const user = await getCurrentUser()

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Dashboard de [Cliente]</h1>
        {/* Tu contenido personalizado aquí */}
      </div>
    </main>
  )
}
```

### Opción 3: Usar un Componente Custom

```typescript
// app/(private)/default.tsx (en la rama custom del cliente)
import { ClientDashboard } from '@/components/custom/features/dashboard/ClientDashboard'

/**
 * Página principal por defecto para [Cliente] CRM.
 */
export default async function DefaultPage() {
  return <ClientDashboard />
}
```

## Ejemplos por Cliente

### Artistealo (`crm-artistealo`)

```typescript
// Redirige a /inbox (dashboard principal)
import { redirect } from 'next/navigation'

export default async function DefaultPage() {
  redirect('/inbox')
}
```

### Prego (`crm-prego`)

```typescript
// Muestra dashboard con cards
import { getCurrentUser } from '@/app/actions/core/auth'
import { Card, ... } from '@/components/core/ui/card'

export default async function DefaultPage() {
  const user = await getCurrentUser()
  // Renderiza dashboard personalizado
  return <DashboardContent user={user} />
}
```

## Reglas Importantes

1. ✅ **NO modificar `page.tsx`** - Es core, se mantiene igual en todas las ramas
2. ✅ **SÍ modificar `default.tsx`** - Es custom, cada fork tiene su versión
3. ✅ **NO modificar `layout.tsx` en forks** - A menos que necesites agregar componentes wrapper (como CRMLayout)
4. ✅ **Mantener estructura** - `page.tsx` siempre importa `DefaultPage` de `default.tsx`

## Ventajas de esta Estrategia

- ✅ **No rompe el fork**: Cada cliente tiene su propia versión de `default.tsx`
- ✅ **No cambia main**: `main` mantiene la versión genérica
- ✅ **Fácil de mantener**: Cambios en `main` se pueden mergear sin conflictos
- ✅ **Flexible**: Cada cliente puede redirigir o renderizar lo que necesite
- ✅ **Consistente**: Todas las ramas usan la misma estructura base

## Flujo de Actualización Sin Conflictos

Para evitar conflictos automáticamente, se usa `.gitattributes` con estrategias de merge:

### Configuración Automática (`.gitattributes`)

El archivo `.gitattributes` está configurado para resolver conflictos automáticamente:

- **Archivos custom** (`default.tsx`, componentes custom): `merge=ours` - Mantiene la versión custom
- **Archivos core** (`page.tsx`, `layout.tsx`): `merge=theirs` - Acepta cambios de main

### Proceso de Actualización

```bash
# 1. Cambiar a la rama custom
git checkout crm-cliente

# 2. Hacer merge desde main
git merge main

# 3. Git resolverá automáticamente los conflictos según .gitattributes
# - default.tsx: mantendrá la versión custom automáticamente
# - page.tsx/layout.tsx: aceptará cambios de main automáticamente

# 4. Si todo está bien, el merge se completa sin intervención
# Si hay otros conflictos no configurados, resolverlos manualmente
```

### Resolución Manual (si es necesario)

Si necesitas resolver conflictos manualmente:

```bash
# Para mantener la versión custom de default.tsx:
git checkout --ours app/(private)/default.tsx
git add app/(private)/default.tsx

# Para aceptar cambios de main en layout.tsx o page.tsx:
git checkout --theirs app/(private)/layout.tsx
git add app/(private)/layout.tsx

# Completar el merge
git commit
```

**Nota sobre terminología Git:**
- `--ours`: versión de la rama actual (custom) cuando estás en `crm-cliente`
- `--theirs`: versión de la rama que estás mergeando (main) cuando estás en `crm-cliente`
