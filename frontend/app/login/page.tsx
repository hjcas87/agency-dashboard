import { redirect } from "next/navigation"
import { getCurrentUser } from "../actions/core/auth"
import { LoginForm } from "@/components/core/features/auth/LoginForm"

export default async function LoginPage() {
  // Si ya está autenticado, redirigir al CRM
  const user = await getCurrentUser()
  if (user) {
    redirect("/crm")
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <LoginForm />
    </div>
  )
}

