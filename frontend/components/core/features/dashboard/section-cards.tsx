import { IconTrendingDown, IconTrendingUp } from '@tabler/icons-react'

import { Badge } from '@/components/core/ui/badge'
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'

import type { DashboardSummary, KpiValue } from '@/app/actions/custom/dashboard'

interface SectionCardsProps {
  summary: DashboardSummary
}

export function SectionCards({ summary }: SectionCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4 dark:*:data-[slot=card]:bg-card">
      <KpiCard
        label="Facturado este mes"
        value={formatArs(summary.revenue_month.current)}
        kpi={summary.revenue_month}
        footerHeadline="Ingresos del mes calendario"
        footerSub="Suma de Facturas AFIP + Comprobantes X no anulados"
      />
      <KpiCard
        label="Pendiente de cobro"
        value={formatArs(summary.pending_to_bill.current)}
        kpi={null}
        footerHeadline="Saldo en presupuestos aceptados"
        footerSub="Lo que queda por facturar para cerrar cada presupuesto"
      />
      <KpiCard
        label="Ticket promedio (mes)"
        value={formatArs(summary.avg_ticket_month.current)}
        kpi={summary.avg_ticket_month}
        footerHeadline="Promedio por comprobante emitido"
        footerSub="Sirve para detectar si el cliente típico crece o se achica"
      />
      <KpiCard
        label="Clientes activos (90d)"
        value={String(parseFloat(summary.active_clients_90d.current))}
        kpi={summary.active_clients_90d}
        footerHeadline="Distintos clientes facturados en 90 días"
        footerSub="Período comparable al cuatrimestre anterior"
      />
    </div>
  )
}

interface KpiCardProps {
  label: string
  value: string
  // `null` skips the trend badge — used for snapshot KPIs (no historical
  // baseline to compare against, like "Pendiente de cobro").
  kpi: KpiValue | null
  footerHeadline: string
  footerSub: string
}

function KpiCard({ label, value, kpi, footerHeadline, footerSub }: KpiCardProps) {
  const trend = kpi ? trendBadge(kpi) : null
  return (
    <Card className="@container/card">
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
          {value}
        </CardTitle>
        {trend && (
          <CardAction>
            <Badge variant="outline">
              {trend.icon}
              {trend.label}
            </Badge>
          </CardAction>
        )}
      </CardHeader>
      <CardFooter className="flex-col items-start gap-1.5 text-sm">
        <div className="line-clamp-1 flex gap-2 font-medium">
          {footerHeadline}
          {trend && <span className="ml-1 text-muted-foreground">{trend.icon}</span>}
        </div>
        <div className="text-muted-foreground">{footerSub}</div>
      </CardFooter>
    </Card>
  )
}

interface Trend {
  icon: React.ReactNode
  label: string
}

function trendBadge(kpi: KpiValue): Trend | null {
  // No previous baseline to compare against — drop the trend badge
  // entirely instead of showing a meaningless "+0%".
  if (kpi.delta_pct === null) return null
  const delta = parseFloat(kpi.delta_pct)
  if (!Number.isFinite(delta)) return null
  const Icon = delta >= 0 ? IconTrendingUp : IconTrendingDown
  const sign = delta > 0 ? '+' : ''
  return {
    icon: <Icon className="size-4" />,
    label: `${sign}${delta.toFixed(1)}%`,
  }
}

const ARS = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 0,
})

function formatArs(value: string): string {
  const n = parseFloat(value)
  return Number.isFinite(n) ? ARS.format(n) : '—'
}
