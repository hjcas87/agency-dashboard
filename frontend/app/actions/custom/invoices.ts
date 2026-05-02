'use server'

import { revalidatePath } from 'next/cache'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface InvoiceLineItem {
  name: string
  amount: string
}

export interface InvoiceObservation {
  code: number
  message: string
}

export interface InvoiceRecord {
  id: number
  proposal_id: number | null
  client_id: number
  client_name: string | null
  receipt_type: number
  concept: number
  issue_date: string
  service_date_from: string | null
  service_date_to: string | null
  total_amount_ars: string
  document_type: number | null
  document_number: number | null
  line_items: InvoiceLineItem[]
  commercial_reference: string | null
  is_internal: boolean
  internal_number: number | null
  cancelled_at: string | null
  cancels_invoice_id: number | null
  cancelled_by_invoice_id: number | null
  afip_invoice_log_id: number | null
  cae: string | null
  cae_expiration: string | null
  afip_success: boolean
  afip_observations: InvoiceObservation[]
  afip_errors: InvoiceObservation[]
  receipt_number: number | null
  point_of_sale: number | null
  created_at: string
  updated_at: string
}

export interface BillableProposal {
  id: number
  name: string
  client_id: number | null
  client_name: string | null
  total_ars: string
  invoiced_ars: string
  remaining_ars: string
  created_at: string
}

export type IssueOutcome =
  | { success: true; data: InvoiceRecord }
  | { success: false; error: string }

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

export async function getInvoices(): Promise<InvoiceRecord[]> {
  try {
    const res = await fetch(`${API_URL}/api/v1/invoices/`, { cache: 'no-store' })
    if (!res.ok) return []
    return (await res.json()) as InvoiceRecord[]
  } catch {
    return []
  }
}

export async function getInvoice(id: number): Promise<InvoiceRecord | null> {
  try {
    const res = await fetch(`${API_URL}/api/v1/invoices/${id}`, { cache: 'no-store' })
    if (!res.ok) return null
    return (await res.json()) as InvoiceRecord
  } catch {
    return null
  }
}

export async function getBillableProposals(): Promise<BillableProposal[]> {
  try {
    const res = await fetch(`${API_URL}/api/v1/invoices/billable-proposals`, {
      cache: 'no-store',
    })
    if (!res.ok) return []
    return (await res.json()) as BillableProposal[]
  } catch {
    return []
  }
}

// Mirrors backend `app.custom.features.invoices.schemas.InvoiceKind`.
// `AFIP` runs the full ARCA flow; `INTERNAL` skips AFIP and produces a
// local-only "Comprobante interno X".
export type InvoiceKind = 'AFIP' | 'INTERNAL'

// Mirrors backend `app.shared.afip.enums.ReceiptType` — only the values
// the operator picks today. The backend defaults to `INVOICE_C` when
// the field is omitted.
export type ReceiptType = 1 | 6 | 11 | 2 | 3 | 7 | 8 | 12 | 13

export interface IssueFromProposalInput {
  proposal_id: number
  issue_date: string // yyyy-mm-dd
  concept: 1 | 2 | 3
  service_date_from?: string
  service_date_to?: string
  commercial_reference?: string
  kind?: InvoiceKind
  receipt_type?: ReceiptType
  // Decimal serialised as string so we never lose precision in JSON.
  // Omit (undefined) → backend defaults to the proposal's remaining
  // balance. The two-decimal pattern matches what the form emits.
  amount?: string
  description?: string
}

export async function issueInvoiceFromProposalAction(
  input: IssueFromProposalInput
): Promise<IssueOutcome> {
  try {
    const res = await fetch(`${API_URL}/api/v1/invoices/from-proposal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { success: false, error: extractErrorMessage(data, 'Error al emitir la factura') }
    }
    const created = (await res.json()) as InvoiceRecord
    revalidatePath('/invoices')
    return { success: true, data: created }
  } catch {
    return { success: false, error: 'Error de conexión con el servidor' }
  }
}

export interface IssueManualInput {
  client_id: number
  issue_date: string
  concept: 1 | 2 | 3
  service_date_from?: string
  service_date_to?: string
  line_items: { name: string; amount: string }[]
  commercial_reference?: string
  kind?: InvoiceKind
  receipt_type?: ReceiptType
}

export async function issueInvoiceManualAction(input: IssueManualInput): Promise<IssueOutcome> {
  try {
    const res = await fetch(`${API_URL}/api/v1/invoices/manual`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      return { success: false, error: extractErrorMessage(data, 'Error al emitir la factura') }
    }
    const created = (await res.json()) as InvoiceRecord
    revalidatePath('/invoices')
    return { success: true, data: created }
  } catch {
    return { success: false, error: 'Error de conexión con el servidor' }
  }
}

export async function cancelInvoiceAction(
  id: number,
  options: { restore?: boolean } = {}
): Promise<IssueOutcome> {
  const path = options.restore ? 'restore' : 'cancel'
  try {
    const res = await fetch(`${API_URL}/api/v1/invoices/${id}/${path}`, {
      method: 'POST',
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      const fallback = options.restore
        ? 'Error al restaurar el comprobante'
        : 'Error al anular el comprobante'
      return { success: false, error: extractErrorMessage(data, fallback) }
    }
    const updated = (await res.json()) as InvoiceRecord
    revalidatePath('/invoices')
    revalidatePath(`/invoices/${id}`)
    return { success: true, data: updated }
  } catch {
    return { success: false, error: 'Error de conexión con el servidor' }
  }
}
