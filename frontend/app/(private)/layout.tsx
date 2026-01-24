import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/app/actions/core/auth'

/**
 * Layout base para rutas privadas (core).
 * Protege automáticamente todas las páginas dentro de (private)/*
 * verificando la autenticación en el servidor.
 * 
 * Las ramas custom pueden extender este layout para agregar
 * componentes específicos como CRMLayout, sidebars, etc.
 * 
 * Uso:
 * - Coloca cualquier página dentro de app/(private)/* y estará automáticamente protegida
 * - Ejemplo: app/(private)/dashboard/page.tsx → /dashboard (protegida)
 * - Ejemplo: app/(private)/profile/page.tsx → /profile (protegida)
 * 
 * Nota: El proxy.ts ya verifica la existencia de la cookie antes de llegar aquí.
 * Este layout verifica que el token sea válido usando getCurrentUser().
 */
export default async function PrivateLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Verificar que el usuario esté autenticado y el token sea válido
  const user = await getCurrentUser()

  // Si no hay usuario válido, redirigir a login
  if (!user) {
    redirect('/login')
  }

  // Si hay usuario válido, renderizar el contenido
  // Las ramas custom pueden extender este layout para agregar
  // componentes específicos como CRMLayout
  return <>{children}</>
}
