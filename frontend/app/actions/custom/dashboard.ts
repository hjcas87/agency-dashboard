'use server'

import { serverFetch } from '@/lib/shared/server-fetch'

export interface KpiValue {
  current: string // Decimal serialized as string
  previous: string
  delta_pct: string | null
}

export interface ChartPoint {
  date: string // yyyy-mm-dd
  afip: string
  internos: string
}

export interface DashboardSummary {
  revenue_month: KpiValue
  pending_to_bill: KpiValue
  avg_ticket_month: KpiValue
  active_clients_90d: KpiValue
  chart: ChartPoint[]
}

const EMPTY_KPI: KpiValue = { current: '0', previous: '0', delta_pct: null }
const EMPTY_SUMMARY: DashboardSummary = {
  revenue_month: EMPTY_KPI,
  pending_to_bill: EMPTY_KPI,
  avg_ticket_month: EMPTY_KPI,
  active_clients_90d: EMPTY_KPI,
  chart: [],
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  try {
    const res = await serverFetch(`/api/v1/dashboard/summary`, {
      cache: 'no-store',
    })
    if (!res.ok) return EMPTY_SUMMARY
    return (await res.json()) as DashboardSummary
  } catch {
    return EMPTY_SUMMARY
  }
}
