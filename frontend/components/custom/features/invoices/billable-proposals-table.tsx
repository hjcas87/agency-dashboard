'use client'

import { useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { IconLoader2, IconReceipt } from '@tabler/icons-react'

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/core/ui/alert-dialog'
import { Button } from '@/components/core/ui/button'
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from '@/components/core/ui/empty'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/core/ui/table'

import {
  issueInvoiceFromProposalAction,
  type BillableProposal,
} from '@/app/actions/custom/invoices'

interface BillableProposalsTableProps {
  proposals: BillableProposal[]
}

export function BillableProposalsTable({ proposals }: BillableProposalsTableProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [target, setTarget] = useState<BillableProposal | null>(null)

  function confirmIssue() {
    if (!target) return
    const proposal = target
    const today = new Date().toISOString().slice(0, 10)
    startTransition(async () => {
      const result = await issueInvoiceFromProposalAction({
        proposal_id: proposal.id,
        issue_date: today,
        concept: 1,
      })
      if (result.success) {
        const cae = result.data.cae ?? '—'
        toast.success(`Factura C N°${result.data.receipt_number ?? '?'} emitida — CAE ${cae}`)
        router.refresh()
      } else {
        toast.error(result.error)
      }
      setTarget(null)
    })
  }

  if (proposals.length === 0) {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyTitle>No hay presupuestos pendientes de facturar</EmptyTitle>
          <EmptyDescription>
            Solo aparecen acá los presupuestos en estado &quot;Aceptado&quot; sin factura emitida.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button asChild variant="outline">
            <a href="/proposals">Ir a Presupuestos</a>
          </Button>
        </EmptyContent>
      </Empty>
    )
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>Cliente</TableHead>
            <TableHead className="text-right">Total ARS</TableHead>
            <TableHead className="w-32" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {proposals.map(proposal => {
            const total = parseFloat(proposal.total_ars)
            return (
              <TableRow key={proposal.id}>
                <TableCell className="font-medium">{proposal.name}</TableCell>
                <TableCell>
                  {proposal.client_name ?? <span className="text-muted-foreground">—</span>}
                </TableCell>
                <TableCell className="text-right">
                  {total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}
                </TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setTarget(proposal)}
                    disabled={isPending}
                  >
                    <IconReceipt data-icon="inline-start" />
                    Facturar
                  </Button>
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>

      <AlertDialog
        open={target !== null}
        onOpenChange={open => {
          if (!open) setTarget(null)
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Emitir Factura C</AlertDialogTitle>
            <AlertDialogDescription>
              Vas a emitir una Factura C contra AFIP para el presupuesto{' '}
              <span className="font-medium text-foreground">{target?.name}</span>
              {target?.client_name && ` a ${target.client_name}`}. La operación es irreversible — el
              CAE queda registrado en AFIP.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isPending}>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={confirmIssue} disabled={isPending}>
              {isPending ? (
                <IconLoader2 className="animate-spin" data-icon="inline-start" />
              ) : (
                <IconReceipt data-icon="inline-start" />
              )}
              {isPending ? 'Emitiendo…' : 'Emitir factura'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
