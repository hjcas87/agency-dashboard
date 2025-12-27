import { MendriWatermark } from "@/components/core/ui/mendri-watermark"

/**
 * Shared layout for authentication pages (login, reset-password).
 * This ensures the Mendri watermark persists between navigation without reloading.
 */
export default function AuthLayoutWrapper({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <MendriWatermark />
      {children}
    </>
  )
}

