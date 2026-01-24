import { getCurrentUser } from '@/app/actions/core/auth'
import { redirect } from 'next/navigation'

/**
 * Página principal de la aplicación.
 * Si el usuario está autenticado, redirige al CRM (/inbox).
 * Si no está autenticado, muestra la página de bienvenida.
 */
export default async function Home() {
  const user = await getCurrentUser()

  // Si el usuario está autenticado, redirigir al CRM
  if (user) {
    redirect('/inbox')
  } else {
    redirect('/login')
  } 
}
