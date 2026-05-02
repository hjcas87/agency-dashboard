'use client'

import { useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { IconCheck, IconChevronDown } from '@tabler/icons-react'

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
import { Badge } from '@/components/core/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/core/ui/dropdown-menu'
import { updateProposalStatusAction } from '@/app/actions/custom/proposals'

// Mirror of `_ALLOWED_TRANSITIONS` in
// backend/app/custom/features/proposals/service.py — keep in sync with the
// matrix used by ProposalEditForm.
const ALLOWED_TRANSITIONS: Record<string, string[]> = {
  draft: ['sent', 'accepted', 'rejected'],
  sent: ['draft', 'accepted', 'rejected'],
  accepted: ['draft'],
  rejected: ['draft'],
}

const STATUS_LABELS: Record<string, string> = {
  draft: 'Borrador',
  sent: 'Enviado',
  accepted: 'Aceptado',
  rejected: 'Rechazado',
}

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  sent: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  accepted: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  rejected: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
}

const TERMINAL_STATUSES = new Set(['accepted', 'rejected'])

// Transitions that reopen edition on a closed proposal — we always confirm
// because they unlock destructive editing of a document the operator may
// have already shared with the client. Direct flow-forward transitions
// (draft→sent, sent→accepted, etc.) skip confirmation per the operator's
// request: "tipo presionar el estado y se despliegue y se guarde".
function requiresConfirmation(current: string, target: string): boolean {
  return target === 'draft' && TERMINAL_STATUSES.has(current)
}

interface ProposalStatusCellProps {
  proposalId: number
  status: string
}

export function ProposalStatusCell({ proposalId, status }: ProposalStatusCellProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [pendingTarget, setPendingTarget] = useState<string | null>(null)

  const allowedTargets = ALLOWED_TRANSITIONS[status] ?? []
  const label = STATUS_LABELS[status] ?? status

  function commit(target: string) {
    startTransition(async () => {
      const result = await updateProposalStatusAction(proposalId, target)
      if (result.success) {
        toast.success(`Estado: "${STATUS_LABELS[target]}"`)
        router.refresh()
      } else {
        toast.error(result.error)
      }
      setPendingTarget(null)
    })
  }

  function handleSelect(target: string) {
    if (target === status) return
    if (requiresConfirmation(status, target)) {
      setPendingTarget(target)
      return
    }
    commit(target)
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            className="group inline-flex items-center gap-1.5 rounded-full focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 disabled:opacity-50"
            disabled={isPending || allowedTargets.length === 0}
            onClick={e => e.stopPropagation()}
          >
            <Badge variant="secondary" className={STATUS_COLORS[status]}>
              {label}
            </Badge>
            {allowedTargets.length > 0 && (
              <IconChevronDown className="size-3 text-muted-foreground transition-transform group-data-[state=open]:rotate-180" />
            )}
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-44">
          {allowedTargets.map(target => (
            <DropdownMenuItem
              key={target}
              className="cursor-pointer"
              onClick={e => {
                e.stopPropagation()
                handleSelect(target)
              }}
            >
              <IconCheck className="size-3.5 opacity-0" />
              {STATUS_LABELS[target]}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <AlertDialog
        open={pendingTarget !== null}
        onOpenChange={open => {
          if (!open) setPendingTarget(null)
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reabrir presupuesto</AlertDialogTitle>
            <AlertDialogDescription>
              Vas a reabrir un presupuesto {label.toLowerCase()} como &quot;Borrador&quot;. Esto
              habilita la edición del documento — si ya se compartió o cerró con el cliente, dejá
              registro antes.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isPending}>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => pendingTarget && commit(pendingTarget)}
              disabled={isPending}
            >
              {isPending ? 'Aplicando…' : 'Confirmar'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
