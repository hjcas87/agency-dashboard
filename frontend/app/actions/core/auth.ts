'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function loginAction(formData: FormData) {
  const email = formData.get('email') as string
  const password = formData.get('password') as string
  const remember = formData.get('remember') === 'on'

  if (!email || !password) {
    // Retornar error usando redirect con query param
    redirect('/login?error=' + encodeURIComponent('Email y contraseña son requeridos'))
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    })

    // Intentar parsear JSON, pero manejar errores si la respuesta no es JSON
    let data: any = {}
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      try {
        data = await response.json()
      } catch (jsonError) {
        // Si falla el parseo JSON, usar el texto de la respuesta
        const text = await response.text()
        redirect(
          '/login?error=' + encodeURIComponent('Error al iniciar sesión: ' + text.substring(0, 100))
        )
      }
    } else {
      // Si no es JSON, leer como texto
      const text = await response.text()
      redirect(
        '/login?error=' + encodeURIComponent('Error al iniciar sesión: ' + text.substring(0, 100))
      )
    }

    if (!response.ok) {
      // Retornar error usando redirect con query param
      redirect(
        '/login?error=' +
          encodeURIComponent(data.detail || data.message || 'Error al iniciar sesión')
      )
    }

    // Guardar token en httpOnly cookie
    const cookieStore = await cookies()
    // Si "recordarme" está marcado, la cookie dura 30 días, sino 30 minutos
    const maxAge = remember ? 30 * 24 * 60 * 60 : 30 * 60 // 30 días o 30 minutos

    cookieStore.set('access_token', data.access_token, {
      httpOnly: true, // ✅ Prevenir acceso desde JavaScript (protección contra XSS)
      secure: process.env.NODE_ENV === 'production', // ✅ Solo HTTPS en producción (protección contra sniffing)
      sameSite: 'lax', // ⚖️ Balance entre seguridad y funcionalidad
      // "strict" sería más seguro pero rompe redirects desde emails/links externos
      // "lax" permite redirects GET cross-site pero bloquea POST/forms (recomendado por OWASP)
      maxAge,
      path: '/', // ✅ Cookie disponible en toda la aplicación
    })

    // Revalidar todos los paths para asegurar que la cookie esté disponible
    // IMPORTANTE: revalidatePath debe ejecutarse ANTES del redirect
    revalidatePath('/', 'layout')
    revalidatePath('/login', 'page')

    // Hacer redirect desde el servidor después de establecer la cookie
    // Esto asegura que la cookie esté disponible cuando se ejecute el layout
    redirect('/')
  } catch (error) {
    // Si es una excepción de redirect, relanzarla
    if (
      error &&
      typeof error === 'object' &&
      'digest' in error &&
      typeof error.digest === 'string' &&
      error.digest.startsWith('NEXT_REDIRECT')
    ) {
      throw error
    }
    console.error('Login error:', error)
    redirect('/login?error=' + encodeURIComponent('Error interno del servidor'))
  }
}

export async function logoutAction() {
  const cookieStore = await cookies()
  cookieStore.delete('access_token')
  redirect('/login')
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
