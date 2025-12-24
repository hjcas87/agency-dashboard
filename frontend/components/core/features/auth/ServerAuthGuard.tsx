import { redirect } from "next/navigation"
import { getCurrentUser } from "@/app/actions/core/auth"

interface ServerAuthGuardProps {
  children: React.ReactNode
}

/**
 * Server Component que protege rutas verificando autenticación en el servidor.
 * Más seguro que el AuthGuard del cliente porque la verificación ocurre en el servidor.
 */
export async function ServerAuthGuard({ children }: ServerAuthGuardProps) {
  const user = await getCurrentUser()

  if (!user) {
    redirect("/login")
  }

  return <>{children}</>
}

