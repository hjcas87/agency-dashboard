'use client'

import { useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { IconLoader2, IconReceipt } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/core/ui/dialog'
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from '@/components/core/ui/empty'
import { Field, FieldGroup, FieldLabel } from '@/components/core/ui/field'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/core/ui/select'
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
  type InvoiceKind,
} from '@/app/actions/custom/invoices'

interface BillableProposalsTableProps {
  proposals: BillableProposal[]
}

// Visible options for the "Tipo de comprobante" select. Only the kinds
// the operator can actually pick today; new entries (Factura A/B) plug
// in here when their flows are wired up.
const COMPROBANTE_OPTIONS: { value: 'C' | 'X'; label: string; description: string }[] = [
  {
    value: 'C',
    label: 'Factura C',
    description: 'Se emite contra AFIP y queda registrada con CAE.',
  },
  {
    value: 'X',
    label: 'Comprobante interno (X)',
    description: 'Solo para control interno. No pasa por AFIP, no tiene validez fiscal.',
  },
]

export function BillableProposalsTable({ proposals }: BillableProposalsTableProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [target, setTarget] = useState<BillableProposal | null>(null)
  const [option, setOption] = useState<'C' | 'X'>('C')

  function open(proposal: BillableProposal) {
    setOption('C')
    setTarget(proposal)
  }

  function confirmIssue() {
    if (!target) return
    const proposal = target
    const today = new Date().toISOString().slice(0, 10)
    const kind: InvoiceKind = option === 'X' ? 'INTERNAL' : 'AFIP'
    startTransition(async () => {
      const result = await issueInvoiceFromProposalAction({
        proposal_id: proposal.id,
        issue_date: today,
        concept: 1,
        kind,
        receipt_type: 11,
      })
      if (result.success) {
        if (result.data.is_internal) {
          const num = result.data.internal_number ?? '?'
          toast.success(`Comprobante interno X N°${num} emitido`)
        } else {
          const cae = result.data.cae ?? '—'
          toast.success(`Factura C N°${result.data.receipt_number ?? '?'} emitida — CAE ${cae}`)
        }
        router.refresh()
        setTarget(null)
      } else {
        toast.error(result.error)
      }
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

  const selectedOption = COMPROBANTE_OPTIONS.find(o => o.value === option)
  const actionLabel = option === 'X' ? 'Emitir comprobante' : 'Emitir factura'
  const inProgressLabel = option === 'X' ? 'Emitiendo comprobante…' : 'Emitiendo factura…'

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>Cliente</TableHead>
            <TableHead>Aceptado el</TableHead>
            <TableHead className="text-right">Total ARS</TableHead>
            <TableHead className="w-32" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {proposals.map(proposal => {
            const total = parseFloat(proposal.total_ars)
            const acceptedAt = proposal.created_at
              ? new Date(proposal.created_at).toLocaleDateString('es-AR')
              : '—'
            return (
              <TableRow key={proposal.id}>
                <TableCell className="font-medium">{proposal.name}</TableCell>
                <TableCell>
                  {proposal.client_name ?? <span className="text-muted-foreground">—</span>}
                </TableCell>
                <TableCell className="text-muted-foreground">{acceptedAt}</TableCell>
                <TableCell className="text-right font-medium">
                  {total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}
                </TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => open(proposal)}
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

      <Dialog
        open={target !== null}
        onOpenChange={open => {
          if (!open) setTarget(null)
        }}
      >
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Generar comprobante</DialogTitle>
            <DialogDescription>
              Para el presupuesto{' '}
              <span className="font-medium text-foreground">{target?.name}</span>
              {target?.client_name ? ` a ${target.client_name}` : ''}.
            </DialogDescription>
          </DialogHeader>

          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="comprobante-kind">Tipo</FieldLabel>
              <Select
                value={option}
                onValueChange={value => setOption(value as 'C' | 'X')}
                disabled={isPending}
              >
                <SelectTrigger id="comprobante-kind">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {COMPROBANTE_OPTIONS.map(opt => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedOption && (
                <p className="text-xs text-muted-foreground">{selectedOption.description}</p>
              )}
            </Field>
          </FieldGroup>

          <DialogFooter>
            <Button
              variant="ghost"
              onClick={() => setTarget(null)}
              disabled={isPending}
            >
              Cancelar
            </Button>
            <Button onClick={confirmIssue} disabled={isPending}>
              {isPending ? (
                <IconLoader2 className="animate-spin" data-icon="inline-start" />
              ) : (
                <IconReceipt data-icon="inline-start" />
              )}
              {isPending ? inProgressLabel : actionLabel}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
