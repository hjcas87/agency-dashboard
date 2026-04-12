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
  const displayedMessagesRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    const msg = searchParams.get('msg')
    const error = searchParams.get('error')

    if (!msg && !error) return

    const messageKey = msg || error
    if (!messageKey) return

    // Only display each unique message once
    if (displayedMessagesRef.current.has(messageKey)) return
    displayedMessagesRef.current.add(messageKey)

    // Display toast
    if (msg) {
      toast.success(msg)
    } else if (error) {
      toast.error(decodeURIComponent(error))
    }

    // Clean URL immediately to prevent re-trigger
    const params = new URLSearchParams(window.location.search)
    params.delete('msg')
    params.delete('error')
    const clean = params.toString()
    const newUrl = clean ? `${window.location.pathname}?${clean}` : window.location.pathname

    // Use window.history.replaceState for instant URL cleanup without triggering re-render
    window.history.replaceState(null, '', newUrl)
  }, [searchParams])

  return null
}

/**
 * Displays toast notifications from URL query parameters.
 * Handles: ?msg= (success), ?error= (error)
 *
 * Single global instance — only one should exist in the app.
 * Wrapped in Suspense to work with Next.js static generation.
 */
export function MessageReader() {
  return (
    <Suspense fallback={null}>
      <MessageReaderInner />
    </Suspense>
  )
}
