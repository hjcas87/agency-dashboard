"use client"

import { useState, useTransition } from "react"
import Link from "next/link"
import { loginAction } from "@/app/actions/core/auth"
import { useBranding } from "./AuthBrandingProvider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/core/ui/card"
import { Button } from "@/components/core/ui/button"
import { Input } from "@/components/core/ui/input"
import { cn } from "@/lib/utils"

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

  // Card styling from branding config
  const cardRounded = branding.formOptions?.cardStyle?.rounded === 'xl' 
    ? 'rounded-xl' 
    : branding.formOptions?.cardStyle?.rounded === '2xl'
    ? 'rounded-2xl'
    : branding.formOptions?.cardStyle?.rounded === 'lg'
    ? 'rounded-lg'
    : branding.formOptions?.cardStyle?.rounded === 'md'
    ? 'rounded-md'
    : branding.formOptions?.cardStyle?.rounded === 'sm'
    ? 'rounded-sm'
    : 'rounded-lg'
    
  const cardShadow = branding.formOptions?.cardStyle?.shadow === 'xl'
    ? 'shadow-xl'
    : branding.formOptions?.cardStyle?.shadow === 'lg'
    ? 'shadow-lg'
    : branding.formOptions?.cardStyle?.shadow === 'md'
    ? 'shadow-md'
    : branding.formOptions?.cardStyle?.shadow === 'sm'
    ? 'shadow-sm'
    : branding.formOptions?.cardStyle?.shadow === 'none'
    ? 'shadow-none'
    : 'shadow-sm'

  return (
    <Card 
      className={cn(className, cardRounded, cardShadow)}
      style={{
        backgroundColor: branding.colors.cardBackground,
        borderColor: branding.colors.border,
      }}
    >
      <CardHeader className="space-y-1">
        {renderLogo && renderLogo(branding)}
        <CardTitle 
          className={`text-2xl ${branding.formOptions?.textAlignment === 'left' ? 'text-left' : 'text-center'}`}
          style={{ color: branding.colors.text }}
        >
          {branding.texts.loginTitle}
        </CardTitle>
        <CardDescription 
          className={branding.formOptions?.textAlignment === 'left' ? 'text-left' : 'text-center'}
          style={{ color: branding.colors.textSecondary }}
        >
          {branding.texts.loginSubtitle}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form action={handleSubmit} className="space-y-5">
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
              className="rounded-lg"
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
              className="rounded-lg"
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
          {/* Remember me checkbox - optional, shown if needed */}
          {branding.formOptions?.showRememberMe && (
            <div className="flex items-center justify-between">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="remember"
                  defaultChecked={true}
                  className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  style={{ accentColor: branding.colors.primary }}
                />
                <span 
                  className="text-sm"
                  style={{ color: branding.colors.text }}
                >
                  {branding.texts.rememberMe || 'Recordarme'}
                </span>
              </label>
              <Link
                href="/reset-password"
                className="text-sm hover:underline"
                style={{ color: branding.colors.primary }}
              >
                {branding.texts.forgotPasswordLink}
              </Link>
            </div>
          )}
          <Button
            type="submit"
            className="w-full cursor-pointer rounded-lg"
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
          {renderFooter && renderFooter(branding)}
        </form>
      </CardContent>
    </Card>
  )
}

