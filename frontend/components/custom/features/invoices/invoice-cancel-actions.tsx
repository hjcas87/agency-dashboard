'use client'

import { IconBan, IconLoader2, IconRotate } from '@tabler/icons-react'
import { useRouter } from 'next/navigation'
import { useTransition } from 'react'
import { toast } from 'sonner'

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/core/ui/alert-dialog'
import { Button } from '@/components/core/ui/button'

import { cancelInvoiceAction, type InvoiceRecord } from '@/app/actions/custom/invoices'

interface InvoiceCancelActionsProps {
  invoice: InvoiceRecord
}

/**
 * Anular / Restaurar buttons rendered on the invoice detail page.
 * Mirrors the dropdown action in the listing.
 *
 * - Internal X non-cancelled → "Anular" with a soft confirmation
 *   (reversible).
 * - Internal X cancelled → "Restaurar" one-click.
 * - AFIP non-cancelled → "Anular vía NC" with a destructive
 *   confirmation (irreversible — AFIP also records the NC).
 * - AFIP cancelled → no button (the cancellation is final; the user
 *   can navigate to the linked NC from the detail card).
 */
export function InvoiceCancelActions({ invoice }: InvoiceCancelActionsProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()

  const isCancelled = Boolean(invoice.cancelled_at)

  // AFIP cancelled: no action surface — UI shows the NC link in the
  // card body. Internal cancelled: offer Restaurar.
  if (isCancelled && !invoice.is_internal) return null

  function handleRestore() {
    startTransition(async () => {
      const result = await cancelInvoiceAction(invoice.id, { restore: true })
      if (result.success) {
        toast.success('Comprobante restaurado.')
        router.refresh()
      } else {
        toast.error(result.error)
      }
    })
  }

  function handleCancel() {
    startTransition(async () => {
      const result = await cancelInvoiceAction(invoice.id)
      if (result.success) {
        if (invoice.is_internal) {
          const docNumber = invoice.internal_number
            ? `X-${String(invoice.internal_number).padStart(8, '0')}`
            : `#${invoice.id}`
          toast.success(`Comprobante ${docNumber} anulado.`)
        } else {
          const ncNum = result.data.receipt_number ?? '?'
          toast.success(`Nota de Crédito C N°${ncNum} emitida — CAE ${result.data.cae ?? '—'}`)
          // The NC is its own invoice — push the operator there so they
          // can immediately print/email the credit note.
          router.push(`/invoices/${result.data.id}`)
          return
        }
        router.refresh()
      } else {
        toast.error(result.error)
      }
    })
  }

  if (isCancelled && invoice.is_internal) {
    return (
      <Button variant="outline" size="sm" onClick={handleRestore} disabled={isPending}>
        {isPending ? (
          <IconLoader2 className="animate-spin" data-icon="inline-start" />
        ) : (
          <IconRotate data-icon="inline-start" />
        )}
        Restaurar
      </Button>
    )
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="outline" size="sm" disabled={isPending}>
          <IconBan data-icon="inline-start" />
          {invoice.is_internal ? 'Anular' : 'Anular vía NC'}
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {invoice.is_internal ? 'Anular comprobante' : 'Anular factura vía Nota de Crédito'}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {invoice.is_internal ? (
              <>
                Vas a anular el comprobante interno{' '}
                <span className="text-foreground">
                  X-
                  {String(invoice.internal_number ?? 0).padStart(8, '0')}
                </span>
                . La fila queda visible pero tachada y marcada como anulada. La acción es reversible
                — podés restaurarla desde el mismo botón.
              </>
            ) : (
              <>
                Vas a emitir una <strong>Nota de Crédito C</strong> contra AFIP asociada a la
                factura{' '}
                <span className="text-foreground">
                  {String(invoice.point_of_sale ?? 0).padStart(4, '0')}-
                  {String(invoice.receipt_number ?? 0).padStart(8, '0')}
                </span>
                . La NC queda registrada con su propio CAE y la factura original quedará marcada
                como anulada en el listado. La operación es <strong>irreversible</strong>: la NC
                también queda en los registros de AFIP.
              </>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>Cancelar</AlertDialogCancel>
          <AlertDialogAction
            onClick={e => {
              e.preventDefault()
              handleCancel()
            }}
            disabled={isPending}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isPending
              ? invoice.is_internal
                ? 'Anulando…'
                : 'Emitiendo NC…'
              : invoice.is_internal
                ? 'Anular'
                : 'Emitir NC y anular'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
