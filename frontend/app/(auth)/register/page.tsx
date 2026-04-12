import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/app/actions/core/auth'
import { AuthBrandingProvider } from '@/components/core/features/auth/AuthBrandingProvider'
import { AuthLayout } from '@/components/core/features/auth/layouts/AuthLayout'
import { MendriFooter } from '@/components/core/ui/mendri-footer'
import { getBrandingConfig } from '@/lib/core/config/branding'
import RegisterCard from './RegisterCard'

export default async function RegisterPage() {
  const user = await getCurrentUser()
  if (user) {
    redirect('/')
  }

  const branding = getBrandingConfig()

  return (
    <AuthBrandingProvider>
      <AuthLayout>
        <RegisterCard />
      </AuthLayout>
    </AuthBrandingProvider>
  )
}
