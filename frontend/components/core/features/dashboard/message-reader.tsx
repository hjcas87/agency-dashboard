'use client'

import { Suspense, useEffect, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { toast } from 'sonner'

/**
 * Internal component that reads search params and displays toasts.
 */
function MessageReaderInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const lastMessageRef = useRef<string | null>(null)

  useEffect(() => {
    // Try useSearchParams first (works for client navigation)
    let msg = searchParams.get('msg')
    let error = searchParams.get('error')

    // Fallback to window.location for full page loads / redirects
    if (!msg && !error) {
      const urlParams = new URLSearchParams(window.location.search)
      msg = urlParams.get('msg')
      error = urlParams.get('error')
    }

    if (!msg && !error) {
      lastMessageRef.current = null
      return
    }

    const messageKey = msg || error
    // Prevent showing same message twice
    if (lastMessageRef.current === messageKey) return

    // Display toast
    if (msg) {
      toast.success(msg)
    } else if (error) {
      toast.error(decodeURIComponent(error))
    }

    lastMessageRef.current = messageKey

    // Clean URL to prevent re-display
    const params = new URLSearchParams(window.location.search)
    params.delete('msg')
    params.delete('error')
    const clean = params.toString()
    const newUrl = clean ? `${window.location.pathname}?${clean}` : window.location.pathname

    router.replace(newUrl, { scroll: false })
  }, [searchParams, router])

  return null
}

/**
 * Displays toast notifications from URL query parameters.
 * Handles: ?msg= (success), ?error= (error)
 *
 * Reacts to URL changes (both client navigation and full page loads).
 * Wrapped in Suspense to work with Next.js static generation.
 */
export function MessageReader() {
  return (
    <Suspense fallback={null}>
      <MessageReaderInner />
    </Suspense>
  )
}
