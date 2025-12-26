"use client"

import { useState, useTransition } from "react"
import { loginAction } from "@/app/actions/core/auth"
import { useBranding } from "./AuthBrandingProvider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/core/ui/card"
import { Button } from "@/components/core/ui/button"
import { Input } from "@/components/core/ui/input"

interface BaseLoginFormProps {
  className?: string
  onSuccess?: () => void
  renderLogo?: (config: ReturnType<typeof useBranding>) => React.ReactNode
  renderFooter?: (config: ReturnType<typeof useBranding>) => React.ReactNode
}

/**
 * Base login form component (core).
 * Provides functionality without hardcoded styles.
 * Styles and layout can be customized via branding config.
 */
export function BaseLoginForm({
  className,
  onSuccess,
  renderLogo,
  renderFooter,
}: BaseLoginFormProps) {
  const branding = useBranding()
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  const handleSubmit = async (formData: FormData) => {
    setError(null)
    startTransition(async () => {
      const result = await loginAction(formData)
      if (result?.error) {
        setError(result.error)
      } else {
        onSuccess?.()
        // loginAction redirige automáticamente si no hay error
      }
    })
  }

  const LogoComponent = branding.logo.component

  return (
    <Card 
      className={className}
      style={{
        backgroundColor: branding.colors.cardBackground,
        borderColor: branding.colors.border,
      }}
    >
      <CardHeader className="space-y-1">
        {renderLogo ? (
          renderLogo(branding)
        ) : (
          <div className="flex items-center justify-center mb-4">
            {LogoComponent ? (
              <LogoComponent className="w-12 h-12" />
            ) : branding.logo.src ? (
              <img
                src={branding.logo.src}
                alt={branding.logo.alt || "Logo"}
                className={`${branding.logo.size === "sm" ? "w-8 h-8" : branding.logo.size === "lg" ? "w-16 h-16" : "w-12 h-12"}`}
              />
            ) : branding.logo.text ? (
              <div
                className={`${branding.logo.size === "sm" ? "w-8 h-8" : branding.logo.size === "lg" ? "w-16 h-16" : "w-12 h-12"} rounded-lg flex items-center justify-center`}
                style={{ backgroundColor: branding.colors.primary }}
              >
                <span
                  className="font-bold text-2xl"
                  style={{ color: "#ffffff" }}
                >
                  {branding.logo.text}
                </span>
              </div>
            ) : null}
          </div>
        )}
        <CardTitle 
          className="text-2xl text-center"
          style={{ color: branding.colors.text }}
        >
          {branding.texts.loginTitle}
        </CardTitle>
        <CardDescription 
          className="text-center"
          style={{ color: branding.colors.textSecondary }}
        >
          {branding.texts.loginSubtitle}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form action={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label 
              htmlFor="email" 
              className="text-sm font-medium"
              style={{ color: branding.colors.text }}
            >
              {branding.texts.emailLabel}
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder={branding.texts.emailPlaceholder}
              required
              disabled={isPending}
            />
          </div>
          <div className="space-y-2">
            <label 
              htmlFor="password" 
              className="text-sm font-medium"
              style={{ color: branding.colors.text }}
            >
              {branding.texts.passwordLabel}
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder={branding.texts.passwordPlaceholder}
              required
              disabled={isPending}
            />
          </div>
          {error && (
            <div
              className="p-3 text-sm rounded-md border"
              style={{
                color: branding.colors.error,
                backgroundColor: `${branding.colors.error}10`,
                borderColor: `${branding.colors.error}30`,
              }}
            >
              {error}
            </div>
          )}
          <Button
            type="submit"
            className="w-full cursor-pointer"
            style={{
              backgroundColor: branding.colors.primary,
              color: "#ffffff",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = branding.colors.primaryHover
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = branding.colors.primary
            }}
            disabled={isPending}
          >
            {isPending ? "Iniciando sesión..." : branding.texts.loginButton}
          </Button>
          {renderFooter ? (
            renderFooter(branding)
          ) : (
            <div className="text-center">
              <a
                href="/reset-password"
                className="text-sm hover:underline"
                style={{ color: branding.colors.primary }}
              >
                {branding.texts.forgotPasswordLink}
              </a>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}

