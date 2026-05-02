'use client'

import { useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { IconBan, IconLoader2, IconRotate } from '@tabler/icons-react'

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
 * Mirrors the dropdown action in the listing — only surfaces for
 * internal X comprobantes (AFIP receipts need a Nota de Crédito and
 * that flow lives elsewhere). Restoration is one-click; cancellation
 * goes through a confirmation dialog because the visual change is
 * obvious enough that an accidental click should be caught.
 */
export function InvoiceCancelActions({ invoice }: InvoiceCancelActionsProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()

  if (!invoice.is_internal) return null

  const isCancelled = Boolean(invoice.cancelled_at)
  const docNumber = invoice.internal_number
    ? `X-${String(invoice.internal_number).padStart(8, '0')}`
    : `#${invoice.id}`

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
        toast.success(`Comprobante ${docNumber} anulado.`)
        router.refresh()
      } else {
        toast.error(result.error)
      }
    })
  }

  if (isCancelled) {
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
          Anular
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Anular comprobante</AlertDialogTitle>
          <AlertDialogDescription>
            Vas a anular el comprobante interno {docNumber}. La fila queda visible pero
            tachada y marcada como anulada. La acción es reversible — podés restaurarla
            desde el mismo botón.
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
            {isPending ? 'Anulando…' : 'Anular'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
