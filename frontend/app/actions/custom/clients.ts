'use server'

import { revalidatePath } from 'next/cache'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// IvaCondition mirrors backend/app/shared/afip/enums.py::IvaCondition.
// Kept as a string-union so the form can accept the raw codes the API
// returns without intermediate mapping.
export type IvaCondition = 'RI' | 'MT' | 'EX' | 'NA' | 'CF' | 'NC'

export interface ClientRecord {
  id: number
  name: string
  company: string | null
  email: string
  phone: string | null
  cuit: string | null
  iva_condition: IvaCondition | null
}

export interface CuitLookupResult {
  cuit: string
  status: string | null
  person_type: string | null
  company_name: string | null
  first_name: string | null
  last_name: string | null
  iva_condition: IvaCondition | null
  fiscal_address: string | null
  fiscal_locality: string | null
  fiscal_province: string | null
  fiscal_postal_code: string | null
}

export type CuitLookupOutcome =
  | { success: true; data: CuitLookupResult }
  | { success: false; error: string; status: number }

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

function buildClientBody(formData: FormData): Record<string, unknown> {
  const name = formData.get('name') as string
  const company = formData.get('company') as string
  const email = formData.get('email') as string
  const phone = formData.get('phone') as string
  const cuit = formData.get('cuit') as string
  const ivaCondition = formData.get('iva_condition') as string

  const body: Record<string, unknown> = { name, email }
  if (company) body.company = company
  if (phone) body.phone = phone
  if (cuit) body.cuit = cuit
  if (ivaCondition) body.iva_condition = ivaCondition
  return body
}

/**
 * Extract a human-readable message from a FastAPI / Pydantic error
 * response. FastAPI returns 422 with `detail` as either a string or an
 * array of `{ type, loc, msg, input, ctx, url }` objects. Rendering that
 * array as a React child crashes the toast — we flatten it here.
 */
function extractErrorMessage(data: unknown, fallback: string): string {
  if (!data || typeof data !== 'object' || !('detail' in data)) return fallback
  const detail = (data as { detail: unknown }).detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const parts = detail
      .map(entry => {
        if (entry && typeof entry === 'object' && 'msg' in entry) {
          const msg = String((entry as { msg: unknown }).msg)
          const loc = (entry as { loc?: unknown }).loc
          const field =
            Array.isArray(loc) && loc.length > 0
              ? loc.filter(part => part !== 'body').join('.')
              : ''
          return field ? `${field}: ${msg}` : msg
        }
        return null
      })
      .filter((s): s is string => Boolean(s))
    if (parts.length > 0) return parts.join(' • ')
  }
  return fallback
}

export async function createClientAction(formData: FormData) {
  const name = formData.get('name') as string
  const email = formData.get('email') as string

  if (!name || !email) {
    return { success: false as const, error: 'Nombre y email son requeridos', data: null }
  }

  try {
    const res = await fetch(`${API_URL}/api/v1/clients/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildClientBody(formData)),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return {
        success: false as const,
        error: extractErrorMessage(data, 'Error al crear el cliente'),
        data: null,
      }
    }

    const created = (await res.json()) as ClientRecord
    revalidatePath('/clients')
    return { success: true as const, error: null, data: created }
  } catch {
    return { success: false as const, error: 'Error de conexión con el servidor', data: null }
  }
}

export async function updateClientAction(id: number, formData: FormData) {
  const name = formData.get('name') as string
  const email = formData.get('email') as string

  if (!name || !email) {
    return { success: false as const, error: 'Nombre y email son requeridos', data: null }
  }

  try {
    const res = await fetch(`${API_URL}/api/v1/clients/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildClientBody(formData)),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return {
        success: false as const,
        error: extractErrorMessage(data, 'Error al actualizar el cliente'),
        data: null,
      }
    }

    const updated = (await res.json()) as ClientRecord
    revalidatePath('/clients')
    return { success: true as const, error: null, data: updated }
  } catch {
    return { success: false as const, error: 'Error de conexión con el servidor', data: null }
  }
}

export async function lookupCuitInAfipAction(cuit: string): Promise<CuitLookupOutcome> {
  // Normalize on the client side so the URL never carries dashes.
  const normalized = cuit.replace(/[-\s]/g, '')
  if (!/^\d{11}$/.test(normalized)) {
    return { success: false, error: 'El CUIT debe tener 11 dígitos.', status: 400 }
  }
  try {
    const res = await fetch(`${API_URL}/api/v1/clients/lookup-cuit/${normalized}`, {
      cache: 'no-store',
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return {
        success: false,
        error: extractErrorMessage(data, 'No se pudo consultar el padrón'),
        status: res.status,
      }
    }
    const data = (await res.json()) as CuitLookupResult
    return { success: true, data }
  } catch {
    return { success: false, error: 'Error de conexión con el servidor', status: 0 }
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
