"use server"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function loginAction(formData: FormData) {
  const email = formData.get("email") as string
  const password = formData.get("password") as string
  const remember = formData.get("remember") === "on"

  if (!email || !password) {
    return { error: "Email y contraseña son requeridos" }
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    })

    const data = await response.json()

    if (!response.ok) {
      return { error: data.detail || "Error al iniciar sesión" }
    }

    // Guardar token en httpOnly cookie
    const cookieStore = await cookies()
    // Si "recordarme" está marcado, la cookie dura 30 días, sino 30 minutos
    const maxAge = remember ? 30 * 24 * 60 * 60 : 30 * 60 // 30 días o 30 minutos
    
    cookieStore.set("access_token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge,
      path: "/",
    })

    // Redirigir al CRM
    redirect("/crm")
  } catch (error) {
    console.error("Login error:", error)
    return { error: "Error interno del servidor" }
  }
}

export async function logoutAction() {
  const cookieStore = await cookies()
  cookieStore.delete("access_token")
  redirect("/login")
}

export async function getCurrentUser() {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value

  if (!token) {
    return null
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      return null
    }

    const data = await response.json()
    return data.user
  } catch (error) {
    console.error("Get user error:", error)
    return null
  }
}

