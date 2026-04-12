'use client'

import React from 'react'
import { Toaster as SonnerToaster, toast } from 'sonner'

export { toast }

export function Toaster(props: React.ComponentProps<typeof SonnerToaster>) {
  return <SonnerToaster {...props} />
}

export function useToast() {
  return {
    addToast: (options: {
      type: 'success' | 'error' | 'info' | 'warning'
      title: string
      description?: string
      duration?: number
    }) => {
      const { type, title, description, duration = 5000 } = options

      switch (type) {
        case 'success':
          toast.success(title, {
            description,
            duration,
          })
          break
        case 'error':
          toast.error(title, {
            description,
            duration,
          })
          break
        case 'warning':
          toast.warning(title, {
            description,
            duration,
          })
          break
        case 'info':
          toast.info(title, {
            description,
            duration,
          })
          break
      }
    },
  }
}
