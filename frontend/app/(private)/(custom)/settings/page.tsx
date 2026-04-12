'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

import { Button } from '@/components/core/ui/button'
import { MessageReader } from '@/components/core/features/dashboard/message-reader'
import { AUTH_MESSAGES } from '@/lib/messages'
import { SETTINGS } from '@/components/core/features/dashboard/settings-config'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export default function SettingsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [hasConnectedStore, setHasConnectedStore] = useState(false)

  const checkStoreStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/tiendanube/stores`)
      if (res.ok) {
        const data = await res.json()
        setHasConnectedStore(data.total > 0)
      }
    } catch {
      // Silently fail — button will default to hidden
    }
  }

  useEffect(() => {
    void checkStoreStatus()
  }, [])

  const handleConnect = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}${SETTINGS.connectStore.endpoints.initiate}`, {
        method: 'GET',
      })
      if (!res.ok) {
        toast.error(AUTH_MESSAGES.storeConnectError.title)
        return
      }
      const data = (await res.json()) as { auth_url: string }
      window.location.href = data.auth_url
    } catch {
      toast.error(AUTH_MESSAGES.storeConnectMissingId.text ?? '')
    } finally {
      setLoading(false)
    }
  }

  const handleDisconnect = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/tiendanube/stores/disconnect`, {
        method: 'POST',
      })
      if (!res.ok && res.status !== 204) {
        throw new Error()
      }
      setHasConnectedStore(false)
      toast.success(AUTH_MESSAGES.storeDisconnect.title)
    } catch {
      toast.error(AUTH_MESSAGES.storeConnectError.title)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="space-y-4">
      <MessageReader />
      <div>
        <h2 className="text-lg font-semibold">{SETTINGS.connectStore.title}</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {SETTINGS.connectStore.description}
        </p>
      </div>

      <div className="flex gap-3">
        <Button onClick={() => void handleConnect()} disabled={loading}>
          {loading ? SETTINGS.connectStore.labels.loading : SETTINGS.connectStore.labels.submit}
        </Button>
        {hasConnectedStore && (
          <Button variant="outline" onClick={() => void handleDisconnect()} disabled={loading}>
            Desconectar tienda
          </Button>
        )}
      </div>
    </section>
  )
}
