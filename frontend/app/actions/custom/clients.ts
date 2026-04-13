'use server'

import { revalidatePath } from 'next/cache'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ClientRecord {
  id: number
  name: string
  company: string | null
  email: string
  phone: string | null
}

export async function getClients(): Promise<ClientRecord[]> {
  try {
    const res = await fetch(`${API_URL}/api/v1/clients/`, {
      cache: 'no-store',
    })
    if (!res.ok) return []
    return res.json() as Promise<ClientRecord[]>
  } catch {
    return [] as ClientRecord[]
  }
}

export async function getClient(id: number): Promise<ClientRecord> {
  const res = await fetch(`${API_URL}/api/v1/clients/${id}`, {
    cache: 'no-store',
  })
  if (!res.ok) {
    throw new Error('Cliente no encontrado')
  }
  return res.json() as Promise<ClientRecord>
}

export async function createClientAction(formData: FormData) {
  const name = formData.get('name') as string
  const company = formData.get('company') as string
  const email = formData.get('email') as string
  const phone = formData.get('phone') as string

  if (!name || !email) {
    return { success: false as const, error: 'Nombre y email son requeridos', data: null }
  }

  try {
    const body: Record<string, unknown> = { name, email }
    if (company) body.company = company
    if (phone) body.phone = phone

    const res = await fetch(`${API_URL}/api/v1/clients/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { success: false as const, error: (data.detail as string) || 'Error al crear el cliente', data: null }
    }

    const created = await res.json() as ClientRecord
    revalidatePath('/clients')
    return { success: true as const, error: null, data: created }
  } catch {
    return { success: false as const, error: 'Error de conexión con el servidor', data: null }
  }
}

export async function updateClientAction(
  id: number,
  formData: FormData
) {
  const name = formData.get('name') as string
  const company = formData.get('company') as string
  const email = formData.get('email') as string
  const phone = formData.get('phone') as string

  if (!name || !email) {
    return { success: false as const, error: 'Nombre y email son requeridos', data: null }
  }

  try {
    const body: Record<string, unknown> = { name, email }
    if (company) body.company = company
    if (phone) body.phone = phone

    const res = await fetch(`${API_URL}/api/v1/clients/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { success: false as const, error: (data.detail as string) || 'Error al actualizar el cliente', data: null }
    }

    const updated = await res.json() as ClientRecord
    revalidatePath('/clients')
    return { success: true as const, error: null, data: updated }
  } catch {
    return { success: false as const, error: 'Error de conexión con el servidor', data: null }
  }
}

export async function deleteClientAction(id: number): Promise<string | null> {
  try {
    const res = await fetch(`${API_URL}/api/v1/clients/${id}`, {
      method: 'DELETE',
    })

    if (!res.ok && res.status !== 204) {
      return 'Error al eliminar el cliente'
    }

    revalidatePath('/clients')
    return null
  } catch {
    return 'Error de conexión con el servidor'
  }
}
