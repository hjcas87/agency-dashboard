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

export type AuthLayout = "centered" | "split-screen" | "full-width"

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
  size?: "sm" | "md" | "lg"
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
  rememberMe?: string // Optional "Remember me" checkbox label
}

export interface BrandingFormOptions {
  showRememberMe?: boolean // Show "Remember me" checkbox
  textAlignment?: "left" | "center" // Text alignment for titles and descriptions
  cardStyle?: {
    rounded?: "sm" | "md" | "lg" | "xl" | "2xl"
    shadow?: "sm" | "md" | "lg" | "xl" | "2xl" | "none"
  }
}

export interface BrandingLayout {
  type: AuthLayout
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
 * Default branding configuration (core).
 * This can be overridden in custom/features/auth/branding.ts
 */
export const defaultBrandingConfig: AuthBrandingConfig = {
  colors: {
    primary: "#2563eb", // blue-600
    primaryHover: "#1d4ed8", // blue-700
    background: "#f9fafb", // gray-50
    cardBackground: "#ffffff", // white
    text: "#111827", // gray-900
    textSecondary: "#6b7280", // gray-500
    border: "#e5e7eb", // gray-200
    error: "#dc2626", // red-600
    success: "#16a34a", // green-600
  },
  logo: {
    text: "O",
    size: "md",
  },
  texts: {
    loginTitle: "Iniciar Sesión",
    loginSubtitle: "Ingresa tus credenciales para acceder al CRM",
    loginButton: "Iniciar Sesión",
    resetPasswordTitle: "Restablecer Contraseña",
    resetPasswordSubtitle: "Ingresa tu email para recibir un enlace de restablecimiento",
    resetPasswordButton: "Enviar Enlace",
    forgotPasswordLink: "¿Olvidaste tu contraseña?",
    backToLogin: "Volver al Login",
    emailLabel: "Email",
    passwordLabel: "Contraseña",
    confirmPasswordLabel: "Confirmar Contraseña",
    emailPlaceholder: "tu@email.com",
    passwordPlaceholder: "••••••••",
  },
  layout: {
    type: "centered",
  },
  formOptions: {
    showRememberMe: false,
    textAlignment: "center",
    cardStyle: {
      rounded: "md",
      shadow: "sm",
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
    // Try to import custom branding config
    // Using dynamic require with error handling to avoid build-time errors
    let customBranding: any
    try {
      customBranding = require("@/lib/custom/features/auth/branding")
    } catch (requireError) {
      // File doesn't exist or can't be loaded, use defaults
      return defaultBrandingConfig
    }
    
    if (customBranding?.brandingConfig) {
      // Merge with defaults (custom overrides defaults)
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
  } catch (error) {
    // Any other error, use defaults
    console.warn("Error loading custom branding config, using defaults:", error)
  }
  
  return defaultBrandingConfig
}

