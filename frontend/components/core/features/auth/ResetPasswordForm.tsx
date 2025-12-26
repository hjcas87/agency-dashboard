"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/core/ui/card"
import { Button } from "@/components/core/ui/button"
import { Input } from "@/components/core/ui/input"

export function ResetPasswordForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get("token")
  
  const [email, setEmail] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<"request" | "confirm">(token ? "confirm" : "request")

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/password-reset/request`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        }
      )

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || "Error al solicitar reseteo")
      }

      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al solicitar reseteo")
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas no coinciden")
      return
    }

    if (newPassword.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres")
      return
    }

    if (!token) {
      setError("Token no válido")
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/password-reset/confirm`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token, new_password: newPassword }),
        }
      )

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || "Error al restablecer contraseña")
      }

      setSuccess(true)
      setTimeout(() => {
        router.push("/login")
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al restablecer contraseña")
    } finally {
      setLoading(false)
    }
  }

  if (step === "request") {
    return (
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-2xl">O</span>
            </div>
          </div>
          <CardTitle className="text-2xl text-center">Restablecer Contraseña</CardTitle>
          <CardDescription className="text-center">
            Ingresa tu email para recibir un enlace de restablecimiento
          </CardDescription>
        </CardHeader>
        <CardContent>
          {success ? (
            <div className="space-y-4">
              <div className="p-4 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md">
                Si el email existe, se ha enviado un enlace de restablecimiento.
              </div>
              <Button
                onClick={() => router.push("/login")}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white cursor-pointer"
              >
                Volver al Login
              </Button>
            </div>
          ) : (
            <form onSubmit={handleRequestReset} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="tu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                {loading ? "Enviando..." : "Enviar Enlace"}
              </Button>
              <div className="text-center">
                <a
                  href="/login"
                  className="text-sm text-blue-600 hover:underline"
                >
                  Volver al Login
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
        <CardTitle className="text-2xl text-center">Nueva Contraseña</CardTitle>
        <CardDescription className="text-center">
          Ingresa tu nueva contraseña
        </CardDescription>
      </CardHeader>
      <CardContent>
        {success ? (
          <div className="space-y-4">
            <div className="p-4 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md">
              Contraseña restablecida exitosamente. Redirigiendo al login...
            </div>
          </div>
        ) : (
          <form onSubmit={handleConfirmReset} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="newPassword" className="text-sm font-medium">
                Nueva Contraseña
              </label>
              <Input
                id="newPassword"
                type="password"
                placeholder="••••••••"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                disabled={loading}
                minLength={8}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium">
                Confirmar Contraseña
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
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
              {loading ? "Restableciendo..." : "Restablecer Contraseña"}
            </Button>
          </form>
        )}
      </CardContent>
    </Card>
  )
}


