'use client'

import { IconLoader2, IconReceipt } from '@tabler/icons-react'
import { useRouter } from 'next/navigation'
import { useEffect, useState, useTransition } from 'react'
import { toast } from 'sonner'

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
import { Input } from '@/components/core/ui/input'
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

const ARS = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })

function formatArs(amount: string | number): string {
  const value = typeof amount === 'string' ? parseFloat(amount) : amount
  return Number.isFinite(value) ? ARS.format(value) : '—'
}

export function BillableProposalsTable({ proposals }: BillableProposalsTableProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [target, setTarget] = useState<BillableProposal | null>(null)
  const [option, setOption] = useState<'C' | 'X'>('C')
  const [amountInput, setAmountInput] = useState('')
  const [descriptionInput, setDescriptionInput] = useState('')

  // Reset the form whenever a fresh proposal is opened. Default amount
  // = remaining (typical case is "bill what's left"); operator overrides
  // for partial billings.
  useEffect(() => {
    if (!target) return
    setOption('C')
    setAmountInput(target.remaining_ars)
    setDescriptionInput('')
  }, [target])

  function open(proposal: BillableProposal) {
    setTarget(proposal)
  }

  function confirmIssue() {
    if (!target) return
    const proposal = target
    const remaining = parseFloat(proposal.remaining_ars)
    const amount = parseFloat(amountInput)
    if (!Number.isFinite(amount) || amount <= 0) {
      toast.error('El importe debe ser mayor a 0.')
      return
    }
    if (amount > remaining + 0.001) {
      toast.error(`El importe excede el restante (${formatArs(remaining)}).`)
      return
    }
    const today = new Date().toISOString().slice(0, 10)
    const kind: InvoiceKind = option === 'X' ? 'INTERNAL' : 'AFIP'
    startTransition(async () => {
      const result = await issueInvoiceFromProposalAction({
        proposal_id: proposal.id,
        issue_date: today,
        concept: 1,
        kind,
        receipt_type: 11,
        amount: amountInput,
        description: descriptionInput.trim() || undefined,
      })
      if (result.success) {
        const newRemaining = remaining - amount
        const remainingMsg =
          newRemaining > 0 ? ` (resta ${formatArs(newRemaining)})` : ' (presupuesto saldado)'
        if (result.data.is_internal) {
          const num = result.data.internal_number ?? '?'
          toast.success(`Comprobante interno X N°${num} emitido${remainingMsg}`)
        } else {
          const cae = result.data.cae ?? '—'
          toast.success(
            `Factura C N°${result.data.receipt_number ?? '?'} emitida — CAE ${cae}${remainingMsg}`
          )
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
            Solo aparecen acá los presupuestos en estado &quot;Aceptado&quot; con saldo pendiente.
            Si facturaste el total, la fila desaparece.
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

  // Real-time preview of the percentage being billed — helps the
  // operator notice mistypes (e.g. extra zero) before clicking emit.
  const targetTotal = target ? parseFloat(target.total_ars) : 0
  const targetRemaining = target ? parseFloat(target.remaining_ars) : 0
  const parsedAmount = parseFloat(amountInput)
  const percentLabel =
    target && Number.isFinite(parsedAmount) && parsedAmount > 0 && targetTotal > 0
      ? `${((parsedAmount / targetTotal) * 100).toFixed(2)}%`
      : null

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>Cliente</TableHead>
            <TableHead>Aceptado el</TableHead>
            <TableHead className="text-right">Total</TableHead>
            <TableHead className="text-right">Facturado</TableHead>
            <TableHead className="text-right">Restante</TableHead>
            <TableHead className="w-32" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {proposals.map(proposal => {
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
                <TableCell className="text-right">{formatArs(proposal.total_ars)}</TableCell>
                <TableCell className="text-right text-muted-foreground">
                  {formatArs(proposal.invoiced_ars)}
                </TableCell>
                <TableCell className="text-right font-medium">
                  {formatArs(proposal.remaining_ars)}
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
              {target && (
                <>
                  {' '}
                  Total {formatArs(target.total_ars)} — restante{' '}
                  <span className="font-medium text-foreground">
                    {formatArs(target.remaining_ars)}
                  </span>
                  .
                </>
              )}
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

            <Field>
              <FieldLabel htmlFor="comprobante-amount">Importe a facturar (ARS)</FieldLabel>
              <Input
                id="comprobante-amount"
                type="number"
                step="0.01"
                min="0"
                max={targetRemaining}
                value={amountInput}
                onChange={e => setAmountInput(e.target.value)}
                disabled={isPending}
              />
              <p className="text-xs text-muted-foreground">
                Default: el restante del presupuesto. Bajalo para facturar parcial (adelanto,
                cuotas, etc.).{' '}
                {percentLabel && (
                  <span className="text-foreground">Equivale al {percentLabel}.</span>
                )}
              </p>
            </Field>

            <Field>
              <FieldLabel htmlFor="comprobante-description">Detalle (opcional)</FieldLabel>
              <Input
                id="comprobante-description"
                placeholder='ej. "Adelanto fase 1"'
                value={descriptionInput}
                onChange={e => setDescriptionInput(e.target.value)}
                disabled={isPending}
              />
              <p className="text-xs text-muted-foreground">
                Si lo dejás vacío, el sistema usa{' '}
                <span className="text-foreground">
                  Adelanto / Saldo / Pago parcial presupuesto «{target?.name}» (NN%)
                </span>{' '}
                según corresponda.
              </p>
            </Field>
          </FieldGroup>

          <DialogFooter>
            <Button variant="ghost" onClick={() => setTarget(null)} disabled={isPending}>
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
