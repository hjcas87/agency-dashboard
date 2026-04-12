'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { AUTH_MESSAGES } from '@/lib/messages'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function loginAction(formData: FormData) {
  const email = formData.get('email') as string
  const password = formData.get('password') as string
  const remember = formData.get('remember') === 'on'

  if (!email || !password) {
    redirect('/login?msg=' + encodeURIComponent(AUTH_MESSAGES.invalidCredentials.title))
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    })

    // Parse response, handle non-JSON gracefully
    let data: Record<string, unknown> = {}
    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      try {
        data = await response.json()
      } catch {
        const text = await response.text()
        redirect('/login?msg=' + encodeURIComponent(text.substring(0, 100)))
      }
    } else {
      const text = await response.text()
      redirect('/login?msg=' + encodeURIComponent(text.substring(0, 100)))
    }

    if (!response.ok) {
      const detail = (data.detail as string) || AUTH_MESSAGES.invalidCredentials.title
      redirect('/login?msg=' + encodeURIComponent(detail))
    }

    // Save token in httpOnly cookie
    const cookieStore = await cookies()
    const maxAge = remember ? 30 * 24 * 60 * 60 : 30 * 60 // 30 days or 30 minutes

    const accessToken = typeof data.access_token === 'string' ? data.access_token : null
    if (!accessToken) {
      redirect('/login?msg=' + encodeURIComponent(AUTH_MESSAGES.sessionExpired.title))
    }

    cookieStore.set('access_token', accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge,
      path: '/',
    })

    // Revalidate paths to ensure cookie is available
    revalidatePath('/', 'layout')
    revalidatePath('/login', 'page')

    // Redirect after setting cookie with welcome message
    redirect('/?msg=' + encodeURIComponent(AUTH_MESSAGES.loginSuccess.title))
  } catch (error) {
    if (
      error &&
      typeof error === 'object' &&
      'digest' in error &&
      typeof (error as { digest?: string }).digest === 'string' &&
      (error as { digest: string }).digest.startsWith('NEXT_REDIRECT')
    ) {
      throw error
    }
    redirect('/login?msg=' + encodeURIComponent(AUTH_MESSAGES.sessionExpired.title))
  }
}

export async function logoutAction() {
  const cookieStore = await cookies()
  cookieStore.delete('access_token')
  redirect('/login')
}

export async function registerAction(formData: FormData) {
  const email = formData.get('email') as string
  const name = formData.get('name') as string
  const password = formData.get('password') as string
  const passwordConfirm = formData.get('passwordConfirm') as string

  if (!email) {
    redirect('/register?msg=' + encodeURIComponent(AUTH_MESSAGES.invalidCredentials.title))
  }
  if (!name) {
    redirect('/register?msg=' + encodeURIComponent(AUTH_MESSAGES.invalidCredentials.title))
  }
  if (!password) {
    redirect('/register?msg=' + encodeURIComponent(AUTH_MESSAGES.registerError.title))
  }
  if (password.length < 8) {
    redirect('/register?msg=' + encodeURIComponent(AUTH_MESSAGES.registerError.title))
  }
  if (password !== passwordConfirm) {
    redirect('/register?msg=' + encodeURIComponent(AUTH_MESSAGES.registerError.title))
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name, password }),
    })

    let data: Record<string, unknown> = {}
    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      try {
        data = await response.json()
      } catch {
        const text = await response.text()
        redirect('/register?msg=' + encodeURIComponent(text.substring(0, 100)))
      }
    } else {
      const text = await response.text()
      redirect('/register?msg=' + encodeURIComponent(text.substring(0, 100)))
    }

    if (!response.ok) {
      const detail = (data.detail as string) || AUTH_MESSAGES.registerError.title
      redirect('/register?msg=' + encodeURIComponent(detail))
    }

    // Registration succeeded — auto-login
    const loginResponse = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!loginResponse.ok) {
      redirect('/login?msg=' + encodeURIComponent(AUTH_MESSAGES.registerSuccess.title))
    }

    const loginData = await loginResponse.json()
    const cookieStore = await cookies()
    const accessToken = typeof loginData.access_token === 'string' ? loginData.access_token : null
    if (!accessToken) {
      redirect('/login?msg=' + encodeURIComponent(AUTH_MESSAGES.sessionExpired.title))
    }

    cookieStore.set('access_token', accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 30 * 60,
      path: '/',
    })

    revalidatePath('/', 'layout')
    redirect('/?msg=' + encodeURIComponent(AUTH_MESSAGES.registerSuccess.title))
  } catch {
    redirect('/register?msg=' + encodeURIComponent(AUTH_MESSAGES.registerError.title))
  }
}

export async function getCurrentUser() {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return null
  }

  try {
    // Usar el token directamente desde la cookie, no fetch con cookies
    // porque fetch desde server actions no envía cookies automáticamente
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 segundos timeout

    const response = await fetch(`${API_URL}/api/v1/auth/me`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      // No usar cache para obtener datos frescos
      cache: 'no-store',
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      return null
    }

    const data = await response.json()
    // El endpoint /api/v1/auth/me retorna el usuario directamente (no envuelto en { user: ... })
    // Verificar que tenga los campos esperados
    if (data && data.id && data.email) {
      return data
    }
    // Si no tiene el formato esperado, retornar null
    console.error('[getCurrentUser] Unexpected response format:', data)
    return null
  } catch (error) {
    // Silenciar errores de conexión para permitir que la página se renderice
    // El usuario simplemente no estará autenticado si el backend no está disponible
    if (error instanceof Error && error.name === 'AbortError') {
      // Timeout - backend no disponible
      return null
    }
    // Otros errores de red también se ignoran silenciosamente
    return null
  }
}
