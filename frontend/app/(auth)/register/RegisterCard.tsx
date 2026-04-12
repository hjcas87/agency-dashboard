'use client'

import { useState, useTransition } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { registerAction } from '@/app/actions/core/auth'
import {
  AuthBrandingProvider,
  useBranding,
} from '@/components/core/features/auth/AuthBrandingProvider'
import { getBrandingConfig } from '@/lib/core/config/branding'

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

function RegisterForm() {
  const branding = useBranding()
  const searchParams = useSearchParams()
  const urlError = searchParams.get('error')

  const [error, setError] = useState<string | null>(urlError)
  const [pending, startTransition] = useTransition()

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

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    const formData = new FormData(e.currentTarget)
    startTransition(() => {
      void registerAction(formData)
    })
  }

  return (
    <Card className={cn(cardRounded, cardShadow)}>
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Crear cuenta</CardTitle>
        <CardDescription>Completá tus datos para registrarte en Mendri</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium">
              Nombre
            </label>
            <Input
              id="name"
              name="name"
              type="text"
              placeholder="Tu nombre"
              disabled={pending}
              required
              className="rounded-lg"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="tu@email.com"
              disabled={pending}
              required
              className="rounded-lg"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              Contraseña
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="Mínimo 8 caracteres"
              disabled={pending}
              required
              minLength={8}
              className="rounded-lg"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="passwordConfirm" className="text-sm font-medium">
              Confirmar contraseña
            </label>
            <Input
              id="passwordConfirm"
              name="passwordConfirm"
              type="password"
              placeholder="Repetí tu contraseña"
              disabled={pending}
              required
              minLength={8}
              className="rounded-lg"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full" disabled={pending}>
            {pending ? 'Creando cuenta...' : 'Crear cuenta'}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            ¿Ya tenés cuenta?{' '}
            <Link href="/login" className="text-primary hover:underline">
              Iniciá sesión
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  )
}

export default function RegisterCard() {
  const branding = getBrandingConfig()

  return (
    <AuthBrandingProvider>
      <RegisterForm />
    </AuthBrandingProvider>
  )
}
