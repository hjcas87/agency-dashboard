'use client'

import Image from 'next/image'
import { useState } from 'react'

/**
 * Mendri watermark logo component.
 * Should be rendered outside of page-specific layouts to avoid reloading on navigation.
 */
export function MendriWatermark() {
  const [imageError, setImageError] = useState(false)

  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2">
      <span className="text-xs text-gray-600">Desarrollado por</span>
      {!imageError ? (
        <Image
          src="/mendri-logo-negro.png"
          alt="Mendri Software"
          width={80}
          height={32}
          className="h-6 w-auto"
          priority
          onError={() => setImageError(true)}
        />
      ) : (
        <span className="text-xs font-semibold text-gray-700">Mendri</span>
      )}
    </div>
  )
}
