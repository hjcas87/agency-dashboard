import { cookies } from 'next/headers'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Wrapper de fetch para server actions/components que inyecta el token JWT
 * desde la cookie httpOnly. Fetch desde el servidor no envía cookies automáticamente.
 */
export async function serverFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  const headers = new Headers(init.headers)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (!headers.has('Content-Type') && init.body) headers.set('Content-Type', 'application/json')

  return fetch(`${API_URL}${path}`, { ...init, headers })
}
