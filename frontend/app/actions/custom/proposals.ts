'use server'

import { revalidatePath } from 'next/cache'

import { serverFetch } from '@/lib/shared/server-fetch'

export interface ProposalTask {
  name: string
  description: string | null
  hours: string
  sort_order: number
}

export interface ProposalRecord {
  id: number
  name: string
  client_id: number | null
  client_name: string | null
  status: string
  hourly_rate_ars: string
  exchange_rate: string
  adjustment_percentage: string
  total_hours: string
  subtotal_ars: string
  adjustment_amount_ars: string
  total_ars: string
  total_usd: string
  created_at: string
  updated_at: string
  sent_at: string | null
  days_until_expiry: number | null
}

export async function getProposals(): Promise<ProposalRecord[]> {
  try {
    const res = await serverFetch(`/api/v1/proposals/`, {
      cache: 'no-store',
    })
    if (!res.ok) return []
    return res.json() as Promise<ProposalRecord[]>
  } catch {
    return [] as ProposalRecord[]
  }
}

export async function getProposal(id: number): Promise<ProposalRecord & { tasks: ProposalTask[] }> {
  const res = await serverFetch(`/api/v1/proposals/${id}`, {
    cache: 'no-store',
  })
  if (!res.ok) {
    throw new Error('Presupuesto no encontrado')
  }
  return res.json() as Promise<ProposalRecord & { tasks: ProposalTask[] }>
}

export interface ProposalCreateData {
  name: string
  client_id: number | null
  hourly_rate_ars: string
  exchange_rate: string
  adjustment_percentage: string
  tasks: ProposalTask[]
}

export async function createProposalAction(data: ProposalCreateData) {
  try {
    const res = await serverFetch(`/api/v1/proposals/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      return { success: false as const, error: (errData.detail as string) || 'Error al crear el presupuesto' }
    }

    revalidatePath('/proposals')
    return { success: true as const, error: null }
  } catch {
    return { success: false as const, error: 'Error de conexión con el servidor' }
  }
}

export async function updateProposalAction(id: number, data: ProposalCreateData) {
  try {
    const res = await serverFetch(`/api/v1/proposals/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      return { success: false as const, error: (errData.detail as string) || 'Error al actualizar el presupuesto' }
    }

    revalidatePath('/proposals')
    return { success: true as const, error: null }
  } catch {
    return { success: false as const, error: 'Error de conexión con el servidor' }
  }
}

export async function updateProposalStatusAction(id: number, status: string) {
  try {
    const res = await serverFetch(`/api/v1/proposals/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      return { success: false as const, error: (errData.detail as string) || 'Error al actualizar el estado' }
    }

    revalidatePath('/proposals')
    return { success: true as const, error: null }
  } catch {
    return { success: false as const, error: 'Error de conexión con el servidor' }
  }
}

export async function deleteProposalAction(id: number): Promise<string | null> {
  try {
    const res = await serverFetch(`/api/v1/proposals/${id}`, {
      method: 'DELETE',
    })

    if (!res.ok && res.status !== 204) {
      return 'Error al eliminar el presupuesto'
    }

    revalidatePath('/proposals')
    return null
  } catch {
    return 'Error de conexión con el servidor'
  }
}

export async function getClientsForSelect(): Promise<{ id: number; name: string }[]> {
  try {
    const res = await serverFetch(`/api/v1/clients/`, {
      cache: 'no-store',
    })
    if (!res.ok) return []
    const clients = await res.json() as { id: number; name: string }[]
    return clients
  } catch {
    return []
  }
}
