'use client'

import { IconCheck, IconX } from '@tabler/icons-react'

import { Badge } from '@/components/core/ui/badge'
import { Button } from '@/components/core/ui/button'
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from '@/components/core/ui/empty'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/core/ui/table'

import type { InvoiceRecord } from '@/app/actions/custom/invoices'

interface InvoicesTableProps {
  invoices: InvoiceRecord[]
}

// AFIP CbteTipo → human label. Only the values this CRM emits today.
// Mirrors backend/app/shared/afip/enums.py::ReceiptType.
const RECEIPT_TYPE_LABELS: Record<number, string> = {
  1: 'Factura A',
  6: 'Factura B',
  11: 'Factura C',
  3: 'NC A',
  8: 'NC B',
  13: 'NC C',
  2: 'ND A',
  7: 'ND B',
  12: 'ND C',
}

function formatReceiptNumber(invoice: InvoiceRecord): string {
  if (invoice.receipt_number === null || invoice.point_of_sale === null) {
    return '—'
  }
  const pos = String(invoice.point_of_sale).padStart(4, '0')
  const num = String(invoice.receipt_number).padStart(8, '0')
  return `${pos}-${num}`
}

export function InvoicesTable({ invoices }: InvoicesTableProps) {
  if (invoices.length === 0) {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyTitle>Todavía no emitiste ninguna factura</EmptyTitle>
          <EmptyDescription>
            Las facturas que emitas desde un presupuesto o manualmente van a aparecer acá.
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Número</TableHead>
          <TableHead>Tipo</TableHead>
          <TableHead>Cliente</TableHead>
          <TableHead>Fecha</TableHead>
          <TableHead className="text-right">Total ARS</TableHead>
          <TableHead>CAE</TableHead>
          <TableHead>Estado</TableHead>
          <TableHead className="w-24" />
        </TableRow>
      </TableHeader>
      <TableBody>
        {invoices.map(invoice => {
          const total = parseFloat(invoice.total_amount_ars)
          const status = invoice.afip_success
            ? invoice.afip_observations.length > 0
              ? 'Con observaciones'
              : 'Aprobada'
            : 'Rechazada'
          const statusVariant = invoice.afip_success
            ? invoice.afip_observations.length > 0
              ? ('outline' as const)
              : ('default' as const)
            : ('destructive' as const)
          return (
            <TableRow key={invoice.id}>
              <TableCell className="font-mono text-sm">{formatReceiptNumber(invoice)}</TableCell>
              <TableCell>
                {RECEIPT_TYPE_LABELS[invoice.receipt_type] ?? `Tipo ${invoice.receipt_type}`}
              </TableCell>
              <TableCell>
                {invoice.client_name ?? <span className="text-muted-foreground">—</span>}
              </TableCell>
              <TableCell>{invoice.issue_date}</TableCell>
              <TableCell className="text-right">
                {total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}
              </TableCell>
              <TableCell className="font-mono text-xs">
                {invoice.cae ? invoice.cae : <span className="text-muted-foreground">—</span>}
              </TableCell>
              <TableCell>
                <Badge variant={statusVariant} className="gap-1">
                  {invoice.afip_success ? <IconCheck /> : <IconX />}
                  {status}
                </Badge>
              </TableCell>
              <TableCell>
                <Button asChild variant="ghost" size="sm">
                  <a href={`/invoices/${invoice.id}`}>Ver</a>
                </Button>
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}
