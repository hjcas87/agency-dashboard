'use client'

import { useState, useTransition } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { registerAction } from '@/app/actions/core/auth'

import { Button } from '@/components/core/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import { Input } from '@/components/core/ui/input'

export default function RegisterPage() {
  const searchParams = useSearchParams()
  const urlError = searchParams.get('error')

  const [error, setError] = useState<string | null>(urlError)
  const [pending, startTransition] = useTransition()

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    const formData = new FormData(e.currentTarget)
    startTransition(() => {
      void registerAction(formData)
    })
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Crear cuenta</CardTitle>
          <CardDescription>
            Completá tus datos para registrarte en Mendri Loyalty
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="name"
                className="mb-2 block text-sm font-medium"
              >
                Nombre
              </label>
              <Input
                id="name"
                name="name"
                type="text"
                placeholder="Tu nombre"
                disabled={pending}
                required
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium"
              >
                Email
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="tu@email.com"
                disabled={pending}
                required
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium"
              >
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
              />
            </div>

            <div>
              <label
                htmlFor="passwordConfirm"
                className="mb-2 block text-sm font-medium"
              >
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
              />
            </div>

            {error && (
              <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={pending}>
              {pending ? 'Creando cuenta...' : 'Crear cuenta'}
            </Button>
          </form>

          <p className="mt-4 text-center text-sm text-muted-foreground">
            ¿Ya tenés cuenta?{' '}
            <Link
              href="/login"
              className="text-primary underline hover:text-primary/80"
            >
              Iniciá sesión
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
