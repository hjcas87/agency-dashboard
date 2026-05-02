import { notFound } from 'next/navigation'
import { IconAlertTriangle, IconArrowLeft, IconCheck } from '@tabler/icons-react'

import { Badge } from '@/components/core/ui/badge'
import { Button } from '@/components/core/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import { Separator } from '@/components/core/ui/separator'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/core/ui/table'

import { getInvoice } from '@/app/actions/custom/invoices'

const RECEIPT_TYPE_LABELS: Record<number, string> = {
  1: 'Factura A',
  6: 'Factura B',
  11: 'Factura C',
}

const CONCEPT_LABELS: Record<number, string> = {
  1: 'Productos',
  2: 'Servicios',
  3: 'Productos y servicios',
}

function formatReceiptNumber(pos: number | null, num: number | null): string {
  if (pos === null || num === null) return '—'
  return `${String(pos).padStart(4, '0')}-${String(num).padStart(8, '0')}`
}

export default async function InvoiceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const invoiceId = parseInt(id, 10)
  if (isNaN(invoiceId)) notFound()

  const invoice = await getInvoice(invoiceId)
  if (!invoice) notFound()

  const total = parseFloat(invoice.total_amount_ars)
  const status = invoice.afip_success
    ? invoice.afip_observations.length > 0
      ? 'Aprobada con observaciones'
      : 'Aprobada'
    : 'Rechazada'
  const statusVariant = invoice.afip_success
    ? invoice.afip_observations.length > 0
      ? ('outline' as const)
      : ('default' as const)
    : ('destructive' as const)

  return (
    <div className="flex w-full flex-col gap-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <a href="/invoices">
            <IconArrowLeft data-icon="inline-start" />
            <span className="sr-only">Volver a facturación</span>
          </a>
        </Button>
        <h1 className="text-lg font-semibold">
          {RECEIPT_TYPE_LABELS[invoice.receipt_type] ?? `Tipo ${invoice.receipt_type}`} N°
          {formatReceiptNumber(invoice.point_of_sale, invoice.receipt_number)}
        </h1>
        <Badge variant={statusVariant} className="ml-auto gap-1">
          {invoice.afip_success ? <IconCheck /> : <IconAlertTriangle />}
          {status}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Datos de la factura</CardTitle>
          <CardDescription>
            Snapshot de lo que se mandó a AFIP. El CAE queda registrado en{' '}
            <span className="font-mono">afip_invoice_log</span>.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="Cliente" value={invoice.client_name ?? '—'} />
          <Field
            label="Concepto"
            value={CONCEPT_LABELS[invoice.concept] ?? `Tipo ${invoice.concept}`}
          />
          <Field label="Fecha de emisión" value={invoice.issue_date} />
          <Field
            label="Total ARS"
            value={total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}
          />
          {invoice.service_date_from && (
            <Field label="Servicio desde" value={invoice.service_date_from} />
          )}
          {invoice.service_date_to && (
            <Field label="Servicio hasta" value={invoice.service_date_to} />
          )}
          <Field
            label="DocTipo / DocNro"
            value={`${invoice.document_type} / ${invoice.document_number}`}
          />
          <Field
            label="CAE"
            value={invoice.cae ? `${invoice.cae} (vto ${invoice.cae_expiration ?? '—'})` : '—'}
            mono
          />
          {invoice.commercial_reference && (
            <Field label="Referencia comercial" value={invoice.commercial_reference} />
          )}
          {invoice.proposal_id && (
            <Field
              label="Presupuesto origen"
              value={
                <a className="underline" href={`/proposals/${invoice.proposal_id}/edit`}>
                  Ver presupuesto N°{invoice.proposal_id}
                </a>
              }
            />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detalle</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Descripción</TableHead>
                <TableHead className="text-right">Monto ARS</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoice.line_items.map((line, index) => (
                <TableRow key={index}>
                  <TableCell>{line.name}</TableCell>
                  <TableCell className="text-right">
                    {parseFloat(line.amount).toLocaleString('es-AR', {
                      style: 'currency',
                      currency: 'ARS',
                    })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Separator className="my-3" />
          <div className="flex items-center justify-end gap-3 text-sm">
            <span className="text-muted-foreground">Total</span>
            <span className="font-semibold">
              {total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}
            </span>
          </div>
        </CardContent>
      </Card>

      {(invoice.afip_observations.length > 0 || invoice.afip_errors.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle>Respuesta de AFIP</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {invoice.afip_errors.map((err, i) => (
              <div key={`err-${i}`} className="flex gap-2 text-sm">
                <Badge variant="destructive">[{err.code}]</Badge>
                <span>{err.message}</span>
              </div>
            ))}
            {invoice.afip_observations.map((obs, i) => (
              <div key={`obs-${i}`} className="flex gap-2 text-sm">
                <Badge variant="outline">[{obs.code}]</Badge>
                <span>{obs.message}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function Field({
  label,
  value,
  mono = false,
}: {
  label: string
  value: React.ReactNode
  mono?: boolean
}) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={mono ? 'font-mono text-sm' : 'text-sm'}>{value}</span>
    </div>
  )
}
