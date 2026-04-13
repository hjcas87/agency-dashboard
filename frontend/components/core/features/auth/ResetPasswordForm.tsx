'use client'

import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import { Button } from '@/components/core/ui/button'
import { Input } from '@/components/core/ui/input'
import { AUTH_MESSAGES, CONTENT_TYPES, FORM_LABELS } from '@/lib/messages'

export function ResetPasswordForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [email, setEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'request' | 'confirm'>(token ? 'confirm' : 'request')

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/password-reset/request`,
        {
          method: 'POST',
          headers: {
            [CONTENT_TYPES.JSON.split(':')[0]]: CONTENT_TYPES.JSON,
          },
          body: JSON.stringify({ email }),
        }
      )

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || AUTH_MESSAGES.errorRequestingReset.description)
      }

      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : AUTH_MESSAGES.errorRequestingReset.description)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (newPassword !== confirmPassword) {
      setError(AUTH_MESSAGES.passwordMismatch.description)
      return
    }

    if (newPassword.length < 8) {
      setError(AUTH_MESSAGES.passwordTooShort.description)
      return
    }

    if (!token) {
      setError(AUTH_MESSAGES.invalidToken.description)
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/password-reset/confirm`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token, new_password: newPassword }),
        }
      )

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || AUTH_MESSAGES.errorConfirmingReset.description)
      }

      setSuccess(true)
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : AUTH_MESSAGES.errorConfirmingReset.description)
    } finally {
      setLoading(false)
    }
  }

  if (step === 'request') {
    return (
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-2xl">O</span>
            </div>
          </div>
          <CardTitle className="text-2xl text-center">{FORM_LABELS.resetPasswordTitle}</CardTitle>
          <CardDescription className="text-center">
            {FORM_LABELS.resetPasswordSubtitle}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {success ? (
            <div className="space-y-4">
              <div className="p-4 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md">
                {AUTH_MESSAGES.passwordResetSuccess.description}
              </div>
              <Button
                onClick={() => router.push('/login')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white cursor-pointer"
              >
                {FORM_LABELS.backToLogin}
              </Button>
            </div>
          ) : (
            <form onSubmit={handleRequestReset} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  {FORM_LABELS.email}
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder={FORM_LABELS.emailPlaceholder}
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  disabled={loading}
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
                disabled={loading}
              >
                {loading ? FORM_LABELS.sendingButton : FORM_LABELS.resetPasswordButton}
              </Button>
              <div className="text-center">
                <a href="/login" className="text-sm text-blue-600 hover:underline">
                  {FORM_LABELS.backToLogin}
                </a>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1">
        <div className="flex items-center justify-center mb-4">
          <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-2xl">O</span>
          </div>
        </div>
        <CardTitle className="text-2xl text-center">{FORM_LABELS.resetPasswordTitle}</CardTitle>
        <CardDescription className="text-center">{FORM_LABELS.resetPasswordSubtitle}</CardDescription>
      </CardHeader>
      <CardContent>
        {success ? (
          <div className="space-y-4">
            <div className="p-4 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md">
              {AUTH_MESSAGES.passwordResetSuccess.description}
            </div>
          </div>
        ) : (
          <form onSubmit={handleConfirmReset} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="newPassword" className="text-sm font-medium">
                {FORM_LABELS.password}
              </label>
              <Input
                id="newPassword"
                type="password"
                placeholder={FORM_LABELS.passwordPlaceholder}
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                required
                disabled={loading}
                minLength={8}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium">
                {FORM_LABELS.confirmPassword}
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder={FORM_LABELS.passwordPlaceholder}
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
                disabled={loading}
                minLength={8}
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
              disabled={loading}
            >
              {loading ? FORM_LABELS.resettingButton : FORM_LABELS.resetPasswordButton}
            </Button>
          </form>
        )}
      </CardContent>
    </Card>
  )
}
