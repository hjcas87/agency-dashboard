import { useCallback, useEffect, useState } from "react"
import { getCurrentUser } from "@/app/actions/core/auth"

interface UseAuthReturn {
  user: Record<string, unknown> | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchUser = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const currentUser = await getCurrentUser()
      setUser(currentUser)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchUser()
  }, [fetchUser])

  return {
    user,
    isAuthenticated: user !== null,
    loading,
    error,
  }
}
