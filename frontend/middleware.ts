import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Si la ruta es /crm o sus subrutas, verificar que haya cookie
  // Solo verifica existencia de cookie, no validez del token
  // La validación del token se hace en los componentes cuando se necesitan datos
  if (pathname.startsWith('/crm')) {
    const token = request.cookies.get('access_token')
    
    // Si no hay token, redirigir a login
    if (!token) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  // No redirigir desde /login automáticamente
  // La página de login verifica si el token es válido usando getCurrentUser()
  // Esto evita loops infinitos si el token es inválido

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/crm/:path*',
  ],
}

