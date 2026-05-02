'use client'

import { useCallback, useEffect, useRef, useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { IconArrowLeft, IconDeviceFloppy, IconPlus, IconTrash } from '@tabler/icons-react'

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
import { Button } from '@/components/core/ui/button'
import { Input } from '@/components/core/ui/input'
import { Label } from '@/components/core/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/core/ui/select'
import { Separator } from '@/components/core/ui/separator'
import { Textarea } from '@/components/core/ui/textarea'

import {
  getClientsForSelect,
  updateProposalAction,
  updateProposalStatusAction,
  type ProposalCurrency,
  type ProposalTask,
} from '@/app/actions/custom/proposals'
import { PROPOSAL_MESSAGES } from '@/lib/messages'

interface ClientOption {
  id: number
  name: string
}

interface ProposalEditFormProps {
  proposal: {
    id: number
    name: string
    client_id: number | null
    client_name: string | null
    status: string
    currency: ProposalCurrency
    hourly_rate_ars: string
    exchange_rate: string
    adjustment_percentage: string
    estimated_days: string | null
    deliverables_summary: string | null
    tasks: ProposalTask[]
  }
}

// Mirror of `_ALLOWED_TRANSITIONS` in
// backend/app/custom/features/proposals/service.py — keep them in sync.
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

function transitionDescription(current: string, target: string): string {
  if (target === 'draft' && TERMINAL_STATUSES.has(current)) {
    return (
      `Vas a reabrir un presupuesto ${STATUS_LABELS[current].toLowerCase()} ` +
      `como "Borrador". Esto habilita la edición del documento — si el ` +
      `presupuesto ya se compartió o cerró con el cliente, dejá registro antes.`
    )
  }
  return `Vas a marcar este presupuesto como "${STATUS_LABELS[target]}". ¿Confirmás?`
}

export function ProposalEditForm({ proposal }: ProposalEditFormProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [formError, setFormError] = useState<string | null>(null)
  const [clients, setClients] = useState<ClientOption[]>([])
  const [name, setName] = useState(proposal.name)
  const [clientId, setClientId] = useState<string>(proposal.client_id?.toString() ?? '__none__')
  const [currency, setCurrency] = useState<ProposalCurrency>(proposal.currency ?? 'ARS')
  const [hourlyRate, setHourlyRate] = useState(proposal.hourly_rate_ars)
  const [exchangeRate, setExchangeRate] = useState(proposal.exchange_rate)
  const [adjustmentPct, setAdjustmentPct] = useState(proposal.adjustment_percentage)
  const [estimatedDays, setEstimatedDays] = useState(proposal.estimated_days ?? '')
  const [deliverablesSummary, setDeliverablesSummary] = useState(proposal.deliverables_summary ?? '')
  const [tasks, setTasks] = useState<ProposalTask[]>(proposal.tasks ?? [])
  const [status, setStatus] = useState(proposal.status)
  const [pendingStatus, setPendingStatus] = useState<string | null>(null)
  const tasksRef = useRef<HTMLDivElement>(null)
  const taskNameRefs = useRef<HTMLInputElement[]>([])

  const isReadOnly = TERMINAL_STATUSES.has(status)
  const allowedTargets = ALLOWED_TRANSITIONS[status] ?? []

  useEffect(() => {
    getClientsForSelect().then(setClients)
  }, [])

  const addTask = useCallback(() => {
    const newIndex = tasks.length
    setTasks(prev => [...prev, { name: '', description: null, hours: '0', sort_order: newIndex }])
    requestAnimationFrame(() => {
      if (tasksRef.current) {
        tasksRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
      taskNameRefs.current[newIndex]?.focus()
    })
  }, [tasks.length])

  const removeTask = useCallback((index: number) => {
    setTasks(prev => prev.filter((_, i) => i !== index).map((t, i) => ({ ...t, sort_order: i })))
  }, [])

  const updateTask = useCallback(
    (index: number, field: keyof ProposalTask, value: string | null) => {
      setTasks(prev => prev.map((t, i) => (i === index ? { ...t, [field]: value } : t)))
    },
    []
  )

  function handleStatusSelect(target: string) {
    if (target === status) return
    setPendingStatus(target)
  }

  function handleStatusConfirm() {
    if (!pendingStatus) return
    const target = pendingStatus
    startTransition(async () => {
      const result = await updateProposalStatusAction(proposal.id, target)
      if (result.success) {
        setStatus(target)
        toast.success(`Estado cambiado a "${STATUS_LABELS[target]}"`)
        router.refresh()
      } else {
        toast.error(result.error)
      }
      setPendingStatus(null)
    })
  }

  const totalHours = tasks.reduce((sum, t) => sum + (parseFloat(t.hours) || 0), 0)
  const subtotal = totalHours * (parseFloat(hourlyRate) || 0)
  const adjAmount = (subtotal * (parseFloat(adjustmentPct) || 0)) / 100
  const totalArs = subtotal + adjAmount
  const totalUsd = exchangeRate ? totalArs / parseFloat(exchangeRate) : 0

  const isValid =
    name.trim() && totalHours > 0 && tasks.every(t => t.name.trim() && parseFloat(t.hours) > 0)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setFormError(null)

    if (isReadOnly) {
      // Defensive — the submit button is hidden in read-only mode, but the
      // user could still hit Enter on a focused input. Make sure we don't
      // ship an update for a closed proposal.
      return
    }

    if (!name.trim()) {
      setFormError('El nombre es requerido')
      return
    }
    if (tasks.length === 0) {
      setFormError('Agregá al menos una tarea')
      return
    }
    if (!tasks.every(t => t.name.trim() && parseFloat(t.hours) > 0)) {
      setFormError('Cada tarea debe tener un nombre y horas válidas')
      return
    }

    const data = {
      name,
      client_id: clientId && clientId !== '__none__' ? parseInt(clientId, 10) : null,
      currency,
      hourly_rate_ars: hourlyRate,
      exchange_rate: exchangeRate,
      adjustment_percentage: adjustmentPct,
      estimated_days: estimatedDays.trim() || null,
      deliverables_summary: deliverablesSummary.trim() || null,
      tasks: tasks.map((t, i) => ({ ...t, sort_order: i })),
    }

    startTransition(async () => {
      const result = await updateProposalAction(proposal.id, data)
      if (result.success) {
        toast.success(PROPOSAL_MESSAGES.updateSuccess.title, {
          description: PROPOSAL_MESSAGES.updateSuccess.description,
        })
        router.push('/proposals')
        router.refresh()
      } else {
        setFormError(result.error)
        toast.error(PROPOSAL_MESSAGES.updateError.title, {
          description: result.error,
        })
      }
    })
  }

  const adjColor =
    parseFloat(adjustmentPct) < 0
      ? 'text-red-600'
      : parseFloat(adjustmentPct) > 0
        ? 'text-green-600'
        : 'text-muted-foreground'
  const adjLabel =
    parseFloat(adjustmentPct) < 0
      ? 'Descuento'
      : parseFloat(adjustmentPct) > 0
        ? 'Recargo'
        : 'Ajuste'

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <a href="/proposals">
            <IconArrowLeft className="size-4" />
          </a>
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">Editar Presupuesto</h1>
          <p className="text-sm text-muted-foreground">
            Modificá los datos de <span className="font-medium">{proposal.name}</span>.
          </p>
        </div>
      </div>

      {/* Status control */}
      <div className="rounded-lg border bg-muted/30 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <Label className="m-0">Estado:</Label>
          <Badge variant="secondary" className={STATUS_COLORS[status]}>
            {STATUS_LABELS[status] ?? status}
          </Badge>
          {allowedTargets.length > 0 && (
            <Select value="" onValueChange={handleStatusSelect} disabled={isPending}>
              <SelectTrigger className="h-8 w-44">
                <SelectValue placeholder="Cambiar a…" />
              </SelectTrigger>
              <SelectContent>
                {allowedTargets.map(target => (
                  <SelectItem key={target} value={target}>
                    {STATUS_LABELS[target]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {isReadOnly && (
            <span className="text-xs text-muted-foreground">
              Edición bloqueada — pasá a Borrador para modificar.
            </span>
          )}
        </div>
      </div>

      <Separator />

      {/* General settings */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="name">
            Nombre <span className="text-destructive">*</span>
          </Label>
          <Input
            id="name"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Nombre del presupuesto"
            required
            disabled={isReadOnly}
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="client">Cliente</Label>
          <Select value={clientId} onValueChange={setClientId} disabled={isReadOnly}>
            <SelectTrigger id="client">
              <SelectValue placeholder="Sin cliente" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">Sin cliente</SelectItem>
              {clients.map(c => (
                <SelectItem key={c.id} value={c.id.toString()}>
                  {c.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="currency">
            Moneda al cliente <span className="text-destructive">*</span>
          </Label>
          <Select
            value={currency}
            onValueChange={value => setCurrency(value as ProposalCurrency)}
            disabled={isReadOnly}
          >
            <SelectTrigger id="currency">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ARS">ARS — Pesos argentinos</SelectItem>
              <SelectItem value="USD">USD — Dólares</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="hourlyRate">Valor por hora (ARS)</Label>
          <Input
            id="hourlyRate"
            type="number"
            step="0.01"
            min="0"
            value={hourlyRate}
            onChange={e => setHourlyRate(e.target.value)}
            disabled={isReadOnly}
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="exchangeRate">Tasa de cambio (1 USD = X ARS)</Label>
          <Input
            id="exchangeRate"
            type="number"
            step="0.01"
            min="0"
            value={exchangeRate}
            onChange={e => setExchangeRate(e.target.value)}
            disabled={isReadOnly}
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="adjustment">
            Ajuste (
            {parseFloat(adjustmentPct) < 0
              ? 'Descuento'
              : parseFloat(adjustmentPct) > 0
                ? 'Recargo'
                : 'Sin ajuste'}
            )
          </Label>
          <div className="flex items-center gap-2">
            <Input
              id="adjustment"
              type="number"
              step="1"
              min="-100"
              max="100"
              value={adjustmentPct}
              onChange={e => setAdjustmentPct(e.target.value)}
              className="w-32"
              disabled={isReadOnly}
            />
            <span className="text-sm text-muted-foreground">%</span>
          </div>
        </div>
      </div>

      {/* Resumen para el cliente (PDF) */}
      <div className="flex flex-col gap-4 rounded-lg border bg-muted/20 p-4">
        <div>
          <h3 className="text-base font-semibold">Resumen para el cliente</h3>
          <p className="text-sm text-muted-foreground">
            Estos campos se imprimen en la página de entregables del PDF.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="estimatedDays">Tiempo de desarrollo</Label>
          <Input
            id="estimatedDays"
            value={estimatedDays}
            onChange={e => setEstimatedDays(e.target.value)}
            placeholder="ej. 30 días hábiles"
            maxLength={64}
            disabled={isReadOnly}
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="deliverablesSummary">Resumen de entregables</Label>
          <Textarea
            id="deliverablesSummary"
            value={deliverablesSummary}
            onChange={e => setDeliverablesSummary(e.target.value)}
            placeholder="Texto que verá el cliente en la sección de entregables. Si lo dejás vacío esa zona del PDF queda en blanco."
            rows={6}
            disabled={isReadOnly}
          />
        </div>
      </div>

      {/* Tasks */}
      <div ref={tasksRef} className="flex flex-col gap-3">
        <div className="sticky top-[5rem] z-50 flex items-center justify-between bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 rounded-lg border px-4 py-3 shadow-md">
          <Label className="text-base font-semibold">Tareas</Label>
          <Button
            type="button"
            size="sm"
            className="bg-emerald-600 text-white hover:bg-emerald-700"
            onClick={addTask}
            disabled={isReadOnly}
          >
            <IconPlus className="size-4" />
            Agregar tarea
          </Button>
        </div>

        <div className="flex flex-col gap-3">
          {tasks.map((task, index) => (
            <div key={index} className="flex flex-col gap-3 rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <Badge variant="outline">Tarea {index + 1}</Badge>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="size-8 text-destructive"
                  onClick={() => removeTask(index)}
                  disabled={tasks.length === 1 || isReadOnly}
                >
                  <IconTrash className="size-4" />
                </Button>
              </div>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
                <div className="flex flex-col gap-2 md:col-span-3">
                  <Label>
                    Nombre <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    ref={el => {
                      taskNameRefs.current[index] = el!
                    }}
                    value={task.name}
                    onChange={e => updateTask(index, 'name', e.target.value)}
                    placeholder="Nombre de la tarea"
                    disabled={isReadOnly}
                  />
                  <Label>Descripción</Label>
                  <Textarea
                    value={task.description ?? ''}
                    onChange={e => updateTask(index, 'description', e.target.value || null)}
                    placeholder="Descripción opcional..."
                    rows={3}
                    disabled={isReadOnly}
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <Label>
                    Horas <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    type="number"
                    step="0.5"
                    min="0"
                    value={task.hours}
                    onChange={e => updateTask(index, 'hours', e.target.value)}
                    disabled={isReadOnly}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Totals panel */}
      <div className="rounded-lg border bg-muted/30 p-4">
        <h3 className="font-semibold mb-3">Resumen</h3>
        <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-sm md:grid-cols-3 lg:grid-cols-6">
          <div className="text-muted-foreground">Total horas</div>
          <div>{totalHours.toFixed(2)} hs</div>
          <div className="text-muted-foreground">Subtotal</div>
          <div>${subtotal.toLocaleString('es-AR')}</div>
          <div className={adjColor}>
            {adjLabel} ({adjustmentPct}%)
          </div>
          <div className={adjColor}>${adjAmount.toLocaleString('es-AR')}</div>
        </div>
        <Separator className="my-3" />
        <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-base md:grid-cols-2">
          <div className="font-semibold">Total ARS</div>
          <div className="font-semibold text-right">${totalArs.toLocaleString('es-AR')}</div>
          <div className="font-semibold">Total USD</div>
          <div className="font-semibold text-right">${totalUsd.toFixed(2)}</div>
        </div>
      </div>

      {formError && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {formError}
        </div>
      )}

      <div className="flex items-center justify-end gap-3">
        <Button
          variant="outline"
          type="button"
          onClick={() => router.push('/proposals')}
          disabled={isPending}
        >
          Cancelar
        </Button>
        {!isReadOnly && (
          <Button type="submit" disabled={isPending || !isValid}>
            <IconDeviceFloppy className="size-4" />
            {isPending ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        )}
      </div>

      {/* Status change confirmation */}
      <AlertDialog
        open={pendingStatus !== null}
        onOpenChange={open => {
          if (!open) setPendingStatus(null)
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Cambiar estado del presupuesto</AlertDialogTitle>
            <AlertDialogDescription>
              {pendingStatus ? transitionDescription(status, pendingStatus) : ''}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isPending}>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleStatusConfirm} disabled={isPending}>
              {isPending ? 'Aplicando…' : 'Confirmar'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </form>
  )
}
