import { getCurrentUser } from '@/app/actions/core/auth'

/**
 * Página principal de rutas privadas (core).
 * 
 * Esta es la versión genérica en main.
 * Cada rama custom puede sobrescribir este archivo para
 * redirigir a su página específica o renderizar su propio contenido.
 */
export default async function PrivatePage() {
  const user = await getCurrentUser()

  // Defensive check: aunque el layout debería proteger esto,
  // agregamos validación para evitar errores si hay timing issues
  if (!user) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
          <h1 className="text-4xl font-bold mb-8 text-center">Core Platform</h1>
          <div className="text-center">
            <p className="text-lg mb-4">Cargando...</p>
          </div>
        </div>
      </main>
    )
  }

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
