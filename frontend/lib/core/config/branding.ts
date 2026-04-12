/**
 * Branding configuration for authentication pages.
 *
 * This configuration allows customization of:
 * - Colors and theme
 * - Logo and branding elements
 * - Text content
 * - Layout styles
 * - Background images
 */
import type React from 'react'

export type AuthLayoutType = 'centered' | 'split-screen' | 'full-width'

export interface BrandingColors {
  primary: string
  primaryHover: string
  secondary?: string
  background: string
  cardBackground: string
  text: string
  textSecondary: string
  border: string
  error: string
  success: string
}

export interface BrandingLogo {
  src?: string
  alt?: string
  component?: React.ComponentType<{ className?: string }>
  text?: string
  size?: 'sm' | 'md' | 'lg'
}

export interface BrandingTexts {
  loginTitle: string
  loginSubtitle: string
  loginButton: string
  resetPasswordTitle: string
  resetPasswordSubtitle: string
  resetPasswordButton: string
  forgotPasswordLink: string
  backToLogin: string
  emailLabel: string
  passwordLabel: string
  confirmPasswordLabel: string
  emailPlaceholder: string
  passwordPlaceholder: string
  rememberMe?: string
}

export interface BrandingFormOptions {
  showRememberMe?: boolean
  textAlignment?: 'left' | 'center'
  cardStyle?: {
    rounded?: 'sm' | 'md' | 'lg' | 'xl' | '2xl'
    shadow?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'none'
  }
}

export interface BrandingLayout {
  type: AuthLayoutType
  backgroundImage?: string
  backgroundOverlay?: string
  leftSideContent?: {
    title?: string
    subtitle?: string
    description?: string
    image?: string
  }
}

export interface AuthBrandingConfig {
  colors: BrandingColors
  logo: BrandingLogo
  texts: BrandingTexts
  layout: BrandingLayout
  formOptions?: BrandingFormOptions
  footer?: {
    show: boolean
    text?: string
    logo?: BrandingLogo
    link?: string
  }
}

/**
 * Default branding configuration.
 * Uses shadcn/ui global CSS variables to stay consistent with the dashboard theme.
 */
export const defaultBrandingConfig: AuthBrandingConfig = {
  colors: {
    primary: 'hsl(var(--primary))',
    primaryHover: 'hsl(var(--primary) / 0.8)',
    background: 'hsl(var(--background))',
    cardBackground: 'hsl(var(--card))',
    text: 'hsl(var(--foreground))',
    textSecondary: 'hsl(var(--muted-foreground))',
    border: 'hsl(var(--border))',
    error: 'hsl(var(--destructive))',
    success: 'hsl(var(--primary))',
  },
  logo: {},
  texts: {
    loginTitle: 'Iniciar sesión',
    loginSubtitle: 'Ingresá tus credenciales para acceder a Mendri',
    loginButton: 'Iniciar sesión',
    resetPasswordTitle: 'Restablecer contraseña',
    resetPasswordSubtitle: 'Ingresá tu email para recibir un enlace de restablecimiento',
    resetPasswordButton: 'Enviar enlace',
    forgotPasswordLink: '¿Olvidaste tu contraseña?',
    backToLogin: 'Volver al login',
    emailLabel: 'Email',
    passwordLabel: 'Contraseña',
    confirmPasswordLabel: 'Confirmar contraseña',
    emailPlaceholder: 'tu@email.com',
    passwordPlaceholder: '••••••••',
  },
  layout: {
    type: 'centered',
  },
  formOptions: {
    showRememberMe: false,
    textAlignment: 'center',
    cardStyle: {
      rounded: 'lg',
      shadow: 'sm',
    },
  },
  footer: {
    show: true,
  },
}

/**
 * Get branding configuration.
 * Allows override from custom/features/auth/branding.ts
 */
export function getBrandingConfig(): AuthBrandingConfig {
  try {
    const customBranding = require('@/lib/custom/features/auth/branding')

    if (customBranding?.brandingConfig) {
      return {
        ...defaultBrandingConfig,
        ...customBranding.brandingConfig,
        colors: {
          ...defaultBrandingConfig.colors,
          ...customBranding.brandingConfig.colors,
        },
        texts: {
          ...defaultBrandingConfig.texts,
          ...customBranding.brandingConfig.texts,
        },
        layout: {
          ...defaultBrandingConfig.layout,
          ...customBranding.brandingConfig.layout,
        },
      }
    }
  } catch {
    // File doesn't exist, use defaults
  }

  return defaultBrandingConfig
}
