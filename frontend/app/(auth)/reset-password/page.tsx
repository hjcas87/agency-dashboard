import { AuthBrandingProvider } from "@/components/core/features/auth/AuthBrandingProvider"
import { AuthLayout } from "@/components/core/features/auth/layouts/AuthLayout"
import { CustomResetPasswordForm } from "@/components/custom/features/auth/CustomResetPasswordForm"
import { MendriFooter } from "@/components/core/ui/mendri-footer"
import { getBrandingConfig } from "@/lib/core/config/branding"

export default function ResetPasswordPage() {
  const branding = getBrandingConfig()

  return (
    <AuthBrandingProvider>
      <AuthLayout>
        <CustomResetPasswordForm />
      </AuthLayout>
      {branding.footer?.show && <MendriFooter />}
    </AuthBrandingProvider>
  )
}

