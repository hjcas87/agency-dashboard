import { redirect } from "next/navigation"
import { getCurrentUser } from "../../actions/core/auth"
import { AuthBrandingProvider } from "@/components/core/features/auth/AuthBrandingProvider"
import { AuthLayout } from "@/components/core/features/auth/layouts/AuthLayout"
import { BaseLoginForm } from "@/components/core/features/auth/BaseLoginForm"
import { MendriFooter } from "@/components/core/ui/mendri-footer"
import { getBrandingConfig } from "@/lib/core/config/branding"

export default async function LoginPage() {
  // Si ya está autenticado, redirigir al CRM
  const user = await getCurrentUser()
  if (user) {
    redirect("/crm")
  }

  const branding = getBrandingConfig()

  return (
    <AuthBrandingProvider>
      <AuthLayout>
        <BaseLoginForm />
      </AuthLayout>
      {branding.footer?.show && <MendriFooter />}
    </AuthBrandingProvider>
  )
}

