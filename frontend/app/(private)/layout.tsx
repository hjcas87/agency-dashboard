import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/app/actions/core/auth'
import { DashboardProvider } from '@/components/core/features/dashboard/DashboardProvider'
import { UserProvider } from '@/components/core/features/dashboard/user-context'

/**
 * Layout base para rutas privadas.
 * Protege automáticamente todas las páginas dentro de (private)/*
 * verificando la autenticación en el servidor, y envuelve el contenido
 * con el dashboard layout (sidebar + header).
 */
export default async function PrivateLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const user = await getCurrentUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <UserProvider user={user}>
      <DashboardProvider>{children}</DashboardProvider>
    </UserProvider>
  )
}
