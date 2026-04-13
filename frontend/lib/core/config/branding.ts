import type React from "react"

export interface AuthBrandingConfig {
  logo: {
    component?: React.ComponentType<{ className?: string }>
    src?: string
    alt?: string
    text?: string
    size?: "sm" | "md" | "lg"
  }
  colors: {
    primary: string
    primaryHover: string
    text: string
    textSecondary: string
    cardBackground: string
    border: string
    success: string
    error: string
  }
  layout: {
    type: "split-screen" | "centered"
    leftSideContent?: {
      title?: string
      subtitle?: string
      description?: string
      image?: string
    }
    backgroundImage?: string
    backgroundOverlay?: string
  }
  texts: {
    loginTitle: string
    loginSubtitle: string
    emailLabel: string
    emailPlaceholder: string
    passwordLabel: string
    passwordPlaceholder: string
    loginButton: string
    forgotPasswordLink: string
    rememberMe?: string
    resetPasswordTitle: string
    resetPasswordSubtitle: string
    resetPasswordButton: string
    backToLogin: string
    confirmPasswordLabel: string
  }
  formOptions?: {
    cardStyle?: {
      rounded?: "sm" | "md" | "lg" | "xl" | "2xl"
      shadow?: "none" | "sm" | "md" | "lg" | "xl"
    }
    showRememberMe?: boolean
  }
  footer?: {
    show?: boolean
  }
}

const defaultConfig: AuthBrandingConfig = {
  logo: {
    text: "Agency Dashboard",
    alt: "Agency Dashboard Logo",
    size: "md",
  },
  colors: {
    primary: "#2563eb",
    primaryHover: "#1d4ed8",
    text: "#0f172a",
    textSecondary: "#64748b",
    cardBackground: "#ffffff",
    border: "#e2e8f0",
    success: "#16a34a",
    error: "#dc2626",
  },
  layout: {
    type: "centered",
  },
  texts: {
    loginTitle: "Iniciar sesión",
    loginSubtitle: "Ingresá a tu cuenta",
    emailLabel: "Email",
    emailPlaceholder: "tu@email.com",
    passwordLabel: "Contraseña",
    passwordPlaceholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022",
    loginButton: "Iniciar sesión",
    forgotPasswordLink: "¿Olvidaste tu contraseña?",
    rememberMe: "Recordarme",
    resetPasswordTitle: "Restablecer contraseña",
    resetPasswordSubtitle: "Ingresá tu nueva contraseña",
    resetPasswordButton: "Restablecer contraseña",
    backToLogin: "Volver al inicio de sesión",
    confirmPasswordLabel: "Confirmar contraseña",
  },
  formOptions: {
    cardStyle: {
      rounded: "2xl",
      shadow: "lg",
    },
    showRememberMe: true,
  },
  footer: {
    show: true,
  },
}

export function getBrandingConfig(): AuthBrandingConfig {
  return defaultConfig
}
