'use client'

import * as React from 'react'
import { Area, AreaChart, CartesianGrid, XAxis } from 'recharts'

import { useIsMobile } from '@/lib/hooks/use-mobile'
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/core/ui/chart'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/core/ui/select'
import { ToggleGroup, ToggleGroupItem } from '@/components/core/ui/toggle-group'

import type { ChartPoint } from '@/app/actions/custom/dashboard'

export const description = 'Facturado por día — Facturas AFIP vs Comprobantes internos'

const chartConfig = {
  total: {
    label: 'Total facturado',
  },
  afip: {
    label: 'Facturas AFIP',
    color: 'var(--primary)',
  },
  internos: {
    label: 'Comprobantes X',
    color: 'var(--primary)',
  },
} satisfies ChartConfig

interface ChartAreaInteractiveProps {
  data: ChartPoint[]
}

// Internal row shape after parsing the Decimal-as-string fields. Kept
// local — the public contract is `ChartPoint`, this is just what we
// hand to Recharts.
interface ChartRow {
  date: string
  afip: number
  internos: number
}

export function ChartAreaInteractive({ data }: ChartAreaInteractiveProps) {
  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState('90d')

  React.useEffect(() => {
    if (isMobile) {
      setTimeRange('7d')
    }
  }, [isMobile])

  // The backend always emits the last 90 days; we slice client-side
  // depending on the toggle. Anchor to the latest point so the window
  // slides forward with the data, not a hardcoded date. Decimal
  // strings are pre-parsed into numbers so Recharts can stack the
  // series — string addition silently produces "0" + "0" = "00".
  const filteredData = React.useMemo<ChartRow[]>(() => {
    if (data.length === 0) return []
    const latest = data[data.length - 1]?.date
    if (!latest) return []
    const referenceDate = new Date(latest)
    const daysToSubtract = timeRange === '30d' ? 30 : timeRange === '7d' ? 7 : 90
    const startDate = new Date(referenceDate)
    startDate.setDate(startDate.getDate() - daysToSubtract)
    return data
      .filter(item => new Date(item.date) >= startDate)
      .map(item => ({
        date: item.date,
        afip: parseFloat(item.afip) || 0,
        internos: parseFloat(item.internos) || 0,
      }))
  }, [data, timeRange])

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle>Facturado</CardTitle>
        <CardDescription>
          <span className="hidden @[540px]/card:block">
            Facturas AFIP y comprobantes internos por día
          </span>
          <span className="@[540px]/card:hidden">Facturado por día</span>
        </CardDescription>
        <CardAction>
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:px-4! @[767px]/card:flex"
          >
            <ToggleGroupItem value="90d">Últimos 3 meses</ToggleGroupItem>
            <ToggleGroupItem value="30d">Últimos 30 días</ToggleGroupItem>
            <ToggleGroupItem value="7d">Últimos 7 días</ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger
              className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
              aria-label="Rango de fechas"
            >
              <SelectValue placeholder="Últimos 3 meses" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">
                Últimos 3 meses
              </SelectItem>
              <SelectItem value="30d" className="rounded-lg">
                Últimos 30 días
              </SelectItem>
              <SelectItem value="7d" className="rounded-lg">
                Últimos 7 días
              </SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer config={chartConfig} className="aspect-auto h-[250px] w-full">
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="fillAfip" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-afip)" stopOpacity={1.0} />
                <stop offset="95%" stopColor="var(--color-afip)" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="fillInternos" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-internos)" stopOpacity={0.8} />
                <stop offset="95%" stopColor="var(--color-internos)" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={value => {
                const date = new Date(value)
                return date.toLocaleDateString('es-AR', {
                  month: 'short',
                  day: 'numeric',
                })
              }}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={value => {
                    return new Date(value as string | number | Date).toLocaleDateString('es-AR', {
                      month: 'short',
                      day: 'numeric',
                    })
                  }}
                  indicator="dot"
                />
              }
            />
            <Area
              dataKey="internos"
              type="natural"
              fill="url(#fillInternos)"
              stroke="var(--color-internos)"
              stackId="a"
            />
            <Area
              dataKey="afip"
              type="natural"
              fill="url(#fillAfip)"
              stroke="var(--color-afip)"
              stackId="a"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
