'use client'

import { useState, useTransition, useCallback, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import {
  IconArrowLeft,
  IconDeviceFloppy,
  IconPlus,
  IconTrash,
} from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import { Input } from '@/components/core/ui/input'
import { Label } from '@/components/core/ui/label'
import { Separator } from '@/components/core/ui/separator'
import { Textarea } from '@/components/core/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/core/ui/select'
import { Badge } from '@/components/core/ui/badge'
import { PROPOSAL_MESSAGES } from '@/lib/messages'
import { createProposalAction, getClientsForSelect, type ProposalTask } from '@/app/actions/custom/proposals'

interface ClientOption {
  id: number
  name: string
}

export function ProposalForm({ initialData }: { initialData?: { name: string; client_id: number | null; hourly_rate_ars: string; exchange_rate: string; adjustment_percentage: string; tasks: ProposalTask[] } }) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [formError, setFormError] = useState<string | null>(null)
  const [clients, setClients] = useState<ClientOption[]>([])
  const [name, setName] = useState(initialData?.name ?? '')
  const [clientId, setClientId] = useState<string>(initialData?.client_id?.toString() ?? '__none__')
  const [hourlyRate, setHourlyRate] = useState(initialData?.hourly_rate_ars ?? '50000')
  const [exchangeRate, setExchangeRate] = useState(initialData?.exchange_rate ?? '1200')
  const [adjustmentPct, setAdjustmentPct] = useState(initialData?.adjustment_percentage ?? '0')
  const [tasks, setTasks] = useState<ProposalTask[]>(
    initialData?.tasks ?? [{ name: '', description: null, hours: '0', sort_order: 0 }]
  )
  const tasksRef = useRef<HTMLDivElement>(null)
  const taskNameRefs = useRef<HTMLInputElement[]>([])

  // Load clients on mount
  useEffect(() => {
    getClientsForSelect().then(setClients)
  }, [])

  const addTask = useCallback(() => {
    const newIndex = tasks.length
    setTasks(prev => [...prev, { name: '', description: null, hours: '0', sort_order: newIndex }])
    // Scroll to tasks container and focus new input on next render
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

  const updateTask = useCallback((index: number, field: keyof ProposalTask, value: string | null) => {
    setTasks(prev => prev.map((t, i) => i === index ? { ...t, [field]: value } : t))
  }, [])

  // Calculations
  const totalHours = tasks.reduce((sum, t) => sum + (parseFloat(t.hours) || 0), 0)
  const subtotal = totalHours * (parseFloat(hourlyRate) || 0)
  const adjAmount = subtotal * (parseFloat(adjustmentPct) || 0) / 100
  const totalArs = subtotal + adjAmount
  const totalUsd = exchangeRate ? totalArs / parseFloat(exchangeRate) : 0

  const isValid = name.trim() && totalHours > 0 && tasks.every(t => t.name.trim() && parseFloat(t.hours) > 0)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setFormError(null)

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
      hourly_rate_ars: hourlyRate,
      exchange_rate: exchangeRate,
      adjustment_percentage: adjustmentPct,
      tasks: tasks.map((t, i) => ({ ...t, sort_order: i })),
    }

    startTransition(async () => {
      const result = await createProposalAction(data)
      if (result.success) {
        toast.success(PROPOSAL_MESSAGES.createSuccess.title, {
          description: PROPOSAL_MESSAGES.createSuccess.description,
        })
        router.push('/proposals')
        router.refresh()
      } else {
        setFormError(result.error)
        toast.error(PROPOSAL_MESSAGES.createError.title, {
          description: result.error,
        })
      }
    })
  }

  const adjColor = parseFloat(adjustmentPct) < 0 ? 'text-red-600' : parseFloat(adjustmentPct) > 0 ? 'text-green-600' : 'text-muted-foreground'
  const adjLabel = parseFloat(adjustmentPct) < 0 ? 'Descuento' : parseFloat(adjustmentPct) > 0 ? 'Recargo' : 'Ajuste'

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <a href="/proposals">
            <IconArrowLeft className="size-4" />
          </a>
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Crear Presupuesto</h1>
          <p className="text-sm text-muted-foreground">
            Completá los datos para generar una nueva cotización.
          </p>
        </div>
      </div>

      <Separator />

      {/* General settings */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="name">Nombre <span className="text-destructive">*</span></Label>
          <Input id="name" value={name} onChange={e => setName(e.target.value)} placeholder="Nombre del presupuesto" required />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="client">Cliente</Label>
          <Select value={clientId} onValueChange={setClientId}>
            <SelectTrigger id="client"><SelectValue placeholder="Sin cliente" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">Sin cliente</SelectItem>
              {clients.map(c => <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="hourlyRate">Valor por hora (ARS) <span className="text-destructive">*</span></Label>
          <Input id="hourlyRate" type="number" step="0.01" min="0" value={hourlyRate} onChange={e => setHourlyRate(e.target.value)} required />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="exchangeRate">Tasa de cambio (1 USD = X ARS) <span className="text-destructive">*</span></Label>
          <Input id="exchangeRate" type="number" step="0.01" min="0" value={exchangeRate} onChange={e => setExchangeRate(e.target.value)} required />
        </div>
      </div>

      {/* Adjustment */}
      <div className="flex flex-col gap-2">
        <Label htmlFor="adjustment">
          Ajuste sobre el subtotal ({parseFloat(adjustmentPct) < 0 ? 'Descuento' : parseFloat(adjustmentPct) > 0 ? 'Recargo' : 'Sin ajuste'})
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
          />
          <span className="text-sm text-muted-foreground">%</span>
        </div>
      </div>

      {/* Tasks */}
      <div ref={tasksRef} className="flex flex-col gap-3">
        <div className="sticky top-[5rem] z-50 flex items-center justify-between bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 rounded-lg border px-4 py-3 shadow-md">
          <Label className="text-base font-semibold">Tareas</Label>
          <Button type="button" size="sm" className="bg-emerald-600 text-white hover:bg-emerald-700" onClick={addTask}>
            <IconPlus className="size-4" />
            Agregar tarea
          </Button>
        </div>

        <div className="flex flex-col gap-3">
          {tasks.map((task, index) => (
          <div key={index} className="flex flex-col gap-3 rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <Badge variant="outline">Tarea {index + 1}</Badge>
              <Button type="button" variant="ghost" size="icon" className="size-8 text-destructive" onClick={() => removeTask(index)} disabled={tasks.length === 1}>
                <IconTrash className="size-4" />
              </Button>
            </div>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
              <div className="flex flex-col gap-2 md:col-span-3">
                <Label>Nombre <span className="text-destructive">*</span></Label>
                <Input ref={el => { taskNameRefs.current[index] = el! }} value={task.name} onChange={e => updateTask(index, 'name', e.target.value)} placeholder="Nombre de la tarea" />
                <Label>Descripción</Label>
                <Textarea value={task.description ?? ''} onChange={e => updateTask(index, 'description', e.target.value || null)} placeholder="Descripción opcional..." rows={3} />
              </div>
              <div className="flex flex-col gap-2">
                <Label>Horas <span className="text-destructive">*</span></Label>
                <Input type="number" step="0.5" min="0" value={task.hours} onChange={e => updateTask(index, 'hours', e.target.value)} />
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
          <div className={adjColor}>{adjLabel} ({adjustmentPct}%)</div>
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

      {/* Error message */}
      {formError && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {formError}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-end gap-3">
        <Button variant="outline" type="button" onClick={() => router.push('/proposals')} disabled={isPending}>
          Cancelar
        </Button>
        <Button type="submit" disabled={isPending || !isValid}>
          <IconDeviceFloppy className="size-4" />
          {isPending ? 'Guardando...' : 'Guardar Presupuesto'}
        </Button>
      </div>
    </form>
  )
}
