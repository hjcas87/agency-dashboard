import { getCurrentUser } from '@/app/actions/core/auth'
import { redirect } from 'next/navigation'

/**
 * Página principal de la aplicación (privada).
 * Si el usuario está autenticado, muestra el dashboard.
 * Si no está autenticado, redirige al login.
 */
export default async function Home() {
  const user = await getCurrentUser()

  // Si no está autenticado, redirigir al login
  if (!user) {
    redirect('/login')
  }

  // Usuario autenticado - mostrar dashboard
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">Core Platform</h1>
        <div className="text-center">
          <p className="text-lg mb-4">Bienvenido, {user.email}</p>
          <p className="text-gray-600">Esta es la página principal privada.</p>
        </div>
      </div>
    </main>
  )
}
