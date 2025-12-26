import { AuthBrandingProvider } from "@/components/core/features/auth/AuthBrandingProvider"
import { AuthLayout } from "@/components/core/features/auth/layouts/AuthLayout"
import { BaseResetPasswordForm } from "@/components/core/features/auth/BaseResetPasswordForm"
import { MendriFooter } from "@/components/core/ui/mendri-footer"
import { getBrandingConfig } from "@/lib/core/config/branding"

export default function ResetPasswordPage() {
  const branding = getBrandingConfig()

  return (
    <AuthBrandingProvider>
      <AuthLayout>
        <BaseResetPasswordForm />
      </AuthLayout>
      {branding.footer?.show && <MendriFooter />}
    </AuthBrandingProvider>
  )
}

