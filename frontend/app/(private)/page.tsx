import { redirect } from 'next/navigation'

/**
 * Página principal de rutas privadas (core).
 * Redirige a la página principal por defecto.
 * 
 * Las ramas custom pueden sobrescribir este archivo para
 * redirigir a su dashboard específico (ej: /inbox, /dashboard, etc.)
 */
export default function PrivatePage() {
  redirect('/')
}
