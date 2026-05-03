import { notFound } from 'next/navigation'
import { IconAlertTriangle, IconArrowLeft, IconCheck, IconInfoCircle } from '@tabler/icons-react'

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

import { getInvoice, type InvoiceRecord } from '@/app/actions/custom/invoices'
import { InvoiceCancelActions } from '@/components/custom/features/invoices/invoice-cancel-actions'

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

function headerLabel(invoice: InvoiceRecord): string {
  if (invoice.is_internal) {
    const num = invoice.internal_number
      ? String(invoice.internal_number).padStart(8, '0')
      : '—'
    return `Presupuesto interno N°X-${num}`
  }
  const type =
    RECEIPT_TYPE_LABELS[invoice.receipt_type] ?? `Tipo ${invoice.receipt_type}`
  return `${type} N°${formatReceiptNumber(invoice.point_of_sale, invoice.receipt_number)}`
}

function statusBadge(invoice: InvoiceRecord): {
  label: string
  variant: 'default' | 'outline' | 'destructive' | 'secondary'
  Icon: typeof IconCheck
} {
  if (invoice.cancelled_at) {
    return { label: 'Anulado', variant: 'destructive', Icon: IconAlertTriangle }
  }
  if (invoice.is_internal) {
    return { label: 'Comprobante interno', variant: 'secondary', Icon: IconInfoCircle }
  }
  if (!invoice.afip_success) {
    return { label: 'Rechazada', variant: 'destructive', Icon: IconAlertTriangle }
  }
  if (invoice.afip_observations.length > 0) {
    return { label: 'Aprobada con observaciones', variant: 'outline', Icon: IconCheck }
  }
  return { label: 'Aprobada', variant: 'default', Icon: IconCheck }
}

export default async function InvoiceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const invoiceId = parseInt(id, 10)
  if (isNaN(invoiceId)) notFound()

  const invoice = await getInvoice(invoiceId)
  if (!invoice) notFound()

  const total = parseFloat(invoice.total_amount_ars)
  const { label: statusLabel, variant: statusVariant, Icon: StatusIcon } = statusBadge(invoice)

  return (
    <div className="flex w-full flex-col gap-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <a href="/invoices">
            <IconArrowLeft data-icon="inline-start" />
            <span className="sr-only">Volver a facturación</span>
          </a>
        </Button>
        <h1 className="text-lg font-semibold">{headerLabel(invoice)}</h1>
        <div className="ml-auto flex items-center gap-2">
          <Badge variant={statusVariant} className="gap-1">
            <StatusIcon className="size-3" />
            {statusLabel}
          </Badge>
          <InvoiceCancelActions invoice={invoice} />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            {invoice.is_internal ? 'Datos del comprobante' : 'Datos de la factura'}
          </CardTitle>
          <CardDescription>
            {invoice.is_internal
              ? 'Comprobante interno sin validez fiscal — no fue autorizado por AFIP.'
              : 'Resumen de lo que se mandó a AFIP. El CAE queda autorizado y registrado en el comprobante.'}
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
          {!invoice.is_internal && (
            <>
              <Field
                label="DocTipo / DocNro"
                value={`${invoice.document_type} / ${invoice.document_number}`}
              />
              <Field
                label="CAE"
                value={
                  invoice.cae ? `${invoice.cae} (vto ${invoice.cae_expiration ?? '—'})` : '—'
                }
              />
            </>
          )}
          {invoice.is_internal && invoice.internal_number !== null && (
            <Field
              label="N° interno"
              value={`X-${String(invoice.internal_number).padStart(8, '0')}`}
            />
          )}
          {invoice.commercial_reference && (
            <Field label="Referencia comercial" value={invoice.commercial_reference} />
          )}
          {invoice.cancelled_by_invoice_id !== null && (
            <Field
              label="Anulada por"
              value={
                <a
                  className="underline"
                  href={`/invoices/${invoice.cancelled_by_invoice_id}`}
                >
                  Ver Nota de Crédito #{invoice.cancelled_by_invoice_id}
                </a>
              }
            />
          )}
          {invoice.cancels_invoice_id !== null && (
            <Field
              label="Anula a"
              value={
                <a
                  className="underline"
                  href={`/invoices/${invoice.cancels_invoice_id}`}
                >
                  Ver factura #{invoice.cancels_invoice_id}
                </a>
              }
            />
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

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm">{value}</span>
    </div>
  )
}
