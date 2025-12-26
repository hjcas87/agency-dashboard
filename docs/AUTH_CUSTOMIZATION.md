# Personalización del Sistema de Autenticación

El sistema de autenticación está diseñado para ser completamente personalizable mientras mantiene la funcionalidad core intacta.

## Arquitectura

### Componentes Core (No modificar)

- `BaseLoginForm` - Formulario base con funcionalidad core
- `BaseResetPasswordForm` - Formulario de reset con funcionalidad core
- `AuthBrandingProvider` - Provider de configuración de branding
- `AuthLayout` - Layouts personalizables (centered, split-screen, full-width)

### Sistema de Configuración

- `lib/core/config/branding.ts` - Configuración por defecto (core)
- `lib/custom/features/auth/branding.ts` - Configuración personalizada (custom)

## Cómo Personalizar

### 1. Crear Configuración de Branding

Crea el archivo `frontend/lib/custom/features/auth/branding.ts`:

```typescript
import { AuthBrandingConfig } from "@/lib/core/config/branding"

export const brandingConfig: Partial<AuthBrandingConfig> = {
  colors: {
    primary: "#3b82f6", // Tu color primario
    primaryHover: "#2563eb",
    // ... otros colores
  },
  logo: {
    src: "/logo.png", // O usa component o text
    alt: "Tu Logo",
  },
  texts: {
    loginTitle: "Iniciar Sesión",
    // ... otros textos
  },
  layout: {
    type: "split-screen", // o "centered" o "full-width"
    backgroundImage: "/auth-background.jpg",
    leftSideContent: {
      title: "¡Bienvenido",
      subtitle: "a nuestro CRM!",
    },
  },
}
```

### 2. Usar en Páginas

Las páginas de auth deben usar `AuthBrandingProvider` y `AuthLayout`:

```typescript
// app/login/page.tsx
import { AuthBrandingProvider } from "@/components/core/features/auth/AuthBrandingProvider"
import { AuthLayout } from "@/components/core/features/auth/layouts/AuthLayout"
import { BaseLoginForm } from "@/components/core/features/auth/BaseLoginForm"

export default function LoginPage() {
  return (
    <AuthBrandingProvider>
      <AuthLayout>
        <BaseLoginForm />
      </AuthLayout>
    </AuthBrandingProvider>
  )
}
```

### 3. Personalización Avanzada

#### Render Props

Puedes usar render props para personalizar completamente el logo y footer:

```typescript
<BaseLoginForm
  renderLogo={(branding) => (
    <div className="custom-logo">
      <YourCustomLogo />
    </div>
  )}
  renderFooter={(branding) => (
    <div className="custom-footer">
      <a href="/custom-link">Custom Link</a>
    </div>
  )}
/>
```

#### Layouts Disponibles

1. **centered** (default) - Formulario centrado en página gris
2. **split-screen** - Pantalla dividida con contenido a la izquierda
3. **full-width** - Layout de ancho completo

#### Ejemplo: Split-Screen Layout

```typescript
layout: {
  type: "split-screen",
  backgroundImage: "/auth-bg.jpg",
  backgroundOverlay: "rgba(59, 130, 246, 0.5)",
  leftSideContent: {
    title: "¡Bienvenido",
    subtitle: "a nuestro CRM!",
    description: "Completa tus datos y empezá a operar",
    image: "/brand-image.jpg",
  },
}
```

## Estructura de Archivos

```
frontend/
├── lib/
│   ├── core/
│   │   └── config/
│   │       └── branding.ts          # Config core (no modificar)
│   └── custom/
│       └── features/
│           └── auth/
│               └── branding.ts      # Tu configuración personalizada
├── components/
│   ├── core/
│   │   └── features/
│   │       └── auth/
│   │           ├── BaseLoginForm.tsx
│   │           ├── BaseResetPasswordForm.tsx
│   │           ├── AuthBrandingProvider.tsx
│   │           └── layouts/
│   │               └── AuthLayout.tsx
│   └── custom/
│       └── features/
│           └── auth/
│               └── CustomLoginPage.tsx  # Ejemplo de página personalizada
└── app/
    ├── login/
    │   └── page.tsx                 # Usa componentes core
    └── reset-password/
        └── page.tsx                 # Usa componentes core
```

## Ejemplos de Personalización

### Ejemplo 1: Cambiar Colores y Logo

```typescript
// lib/custom/features/auth/branding.ts
export const brandingConfig = {
  colors: {
    primary: "#8b5cf6", // Purple
    primaryHover: "#7c3aed",
    // ...
  },
  logo: {
    src: "/my-logo.svg",
    alt: "My Company",
  },
}
```

### Ejemplo 2: Split-Screen con Imagen de Fondo

```typescript
export const brandingConfig = {
  layout: {
    type: "split-screen",
    backgroundImage: "/auth-background.jpg",
    backgroundOverlay: "rgba(0, 0, 0, 0.4)",
    leftSideContent: {
      title: "¡Bienvenido",
      subtitle: "a nuestro CRM!",
      description: "Sistema de gestión integral",
    },
  },
}
```

### Ejemplo 3: Logo como Componente React

```typescript
// components/custom/features/auth/MyLogo.tsx
export function MyLogo({ className }: { className?: string }) {
  return (
    <div className={className}>
      <img src="/logo.svg" alt="Logo" />
    </div>
  )
}

// branding.ts
import { MyLogo } from "@/components/custom/features/auth/MyLogo"

export const brandingConfig = {
  logo: {
    component: MyLogo,
  },
}
```

## Ventajas del Sistema

1. **Funcionalidad Core Intacta** - La lógica de autenticación nunca se modifica
2. **Fácil Personalización** - Solo necesitas crear un archivo de configuración
3. **Escalable** - Puedes personalizar desde colores hasta layouts completos
4. **Mantenible** - Actualizaciones del core no afectan tu personalización
5. **Type-Safe** - TypeScript garantiza que la configuración sea correcta

## Mejores Prácticas

1. **No modificar componentes core** - Usa configuración o render props
2. **Mantén branding.ts simple** - Solo configuración, no lógica
3. **Usa imágenes optimizadas** - Para backgrounds y logos
4. **Prueba en diferentes tamaños** - Especialmente split-screen
5. **Mantén accesibilidad** - Colores con buen contraste

## Troubleshooting

### La configuración no se aplica

1. Verifica que el archivo esté en `lib/custom/features/auth/branding.ts`
2. Asegúrate de exportar `brandingConfig` (no `branding`)
3. Reinicia el servidor de desarrollo

### Los estilos no se aplican correctamente

1. Verifica que `AuthBrandingProvider` envuelva tus componentes
2. Revisa que los colores estén en formato hexadecimal válido
3. Usa `style` props en lugar de clases cuando sea necesario

### El layout no se ve bien

1. Verifica que las imágenes existan en `public/`
2. Ajusta `backgroundOverlay` para mejor legibilidad
3. Prueba diferentes tipos de layout

