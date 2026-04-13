'use client'

import { useState, useTransition } from 'react'
import { useSearchParams } from 'next/navigation'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import { Button } from '@/components/core/ui/button'
import { Input } from '@/components/core/ui/input'
import { loginAction } from '@/app/actions/core/auth'
import { FORM_LABELS } from '@/lib/messages'

export function LoginForm() {
  const searchParams = useSearchParams()
  const errorFromUrl = searchParams.get('error')
  const [error, setError] = useState<string | null>(errorFromUrl)
  const [isPending, startTransition] = useTransition()

  const handleSubmit = async (formData: FormData) => {
    setError(null)
    startTransition(async () => {
      await loginAction(formData)
    })
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1">
        <div className="flex items-center justify-center mb-4">
          <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-2xl">O</span>
          </div>
        </div>
        <CardTitle className="text-2xl text-center">{FORM_LABELS.loginTitle}</CardTitle>
        <CardDescription className="text-center">
          {FORM_LABELS.loginSubtitle}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form action={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              {FORM_LABELS.email}
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder={FORM_LABELS.emailPlaceholder}
              required
              disabled={isPending}
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              {FORM_LABELS.password}
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder={FORM_LABELS.passwordPlaceholder}
              required
              disabled={isPending}
            />
          </div>
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
              {error}
            </div>
          )}
          <Button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white cursor-pointer"
            disabled={isPending}
          >
            {isPending ? FORM_LABELS.signingIn : FORM_LABELS.loginButton}
          </Button>
          <div className="text-center">
            <a href="/reset-password" className="text-sm text-blue-600 hover:underline">
              {FORM_LABELS.forgotPasswordLink}
            </a>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
