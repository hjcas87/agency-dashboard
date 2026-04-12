'use client'

import { useState } from 'react'

import { Button } from '@/components/core/ui/button'
import { SETTINGS } from '@/components/core/features/dashboard/settings-config'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export default function SettingsPage() {
  return (
    <div className="max-w-2xl">
      <ConnectStoreSection />
    </div>
  )
}

function ConnectStoreSection() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleConnect = async () => {
    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_URL}${SETTINGS.connectStore.endpoints.initiate}`, {
        method: 'GET',
      })

      if (!res.ok) {
        throw new Error(SETTINGS.connectStore.validation.error)
      }

      const data = (await res.json()) as { auth_url: string }
      // Redirect user to Tiendanube — they select their store there
      window.location.href = data.auth_url
    } catch {
      setError(SETTINGS.connectStore.validation.unexpected)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">{SETTINGS.connectStore.title}</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {SETTINGS.connectStore.description}
        </p>
      </div>

      <Button onClick={() => void handleConnect()} disabled={loading}>
        {loading ? SETTINGS.connectStore.labels.loading : SETTINGS.connectStore.labels.submit}
      </Button>

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}
    </section>
  )
}
