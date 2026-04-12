'use client'

import { loginAction } from '@/app/actions/core/auth'
import { Button } from '@/components/core/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import { Input } from '@/components/core/ui/input'
import { cn } from '@/lib/utils'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useState, useTransition } from 'react'
import { useBranding } from './AuthBrandingProvider'

interface BaseLoginFormProps {
  className?: string
  onSuccess?: () => void
}

/**
 * Base login form component (core).
 * Uses shadcn/ui theme colors — styling comes from the global theme.
 * Text content comes from branding config.
 */
export function BaseLoginForm({ className, onSuccess }: BaseLoginFormProps) {
  const branding = useBranding()
  const searchParams = useSearchParams()
  const error = searchParams.get('error')
  const [isPending, startTransition] = useTransition()
  const [formError, setFormError] = useState<string | null>(null)

  const LogoComponent = branding.logo.component

  const cardRounded =
    branding.formOptions?.cardStyle?.rounded === 'xl'
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

  const cardShadow =
    branding.formOptions?.cardStyle?.shadow === 'xl'
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
    <Card className={cn(cardRounded, cardShadow, className)}>
      <CardHeader className="space-y-1">
        <CardTitle className="text-center text-2xl">
          {branding.texts.loginTitle}
        </CardTitle>
        <CardDescription className="text-center">
          {branding.texts.loginSubtitle}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form action={loginAction} className="space-y-5">
          {(error || formError) && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
              {error || formError}
            </div>
          )}
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              {branding.texts.emailLabel}
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder={branding.texts.emailPlaceholder}
              required
              className="rounded-lg"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              {branding.texts.passwordLabel}
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder={branding.texts.passwordPlaceholder}
              required
              className="rounded-lg"
            />
          </div>
          {branding.formOptions?.showRememberMe && (
            <div className="flex items-center justify-between">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="remember"
                  defaultChecked
                  className="h-4 w-4 rounded border-border text-primary accent-primary"
                />
                <span className="text-sm">
                  {branding.texts.rememberMe || 'Recordarme'}
                </span>
              </label>
              <Link href="/reset-password" className="text-sm text-primary hover:underline">
                {branding.texts.forgotPasswordLink}
              </Link>
            </div>
          )}
          <Button
            type="submit"
            disabled={isPending}
            className="w-full cursor-pointer rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isPending ? 'Iniciando sesión...' : branding.texts.loginButton}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            ¿No tenés cuenta?{' '}
            <Link href="/register" className="text-primary hover:underline">
              Creá tu cuenta
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  )
}
