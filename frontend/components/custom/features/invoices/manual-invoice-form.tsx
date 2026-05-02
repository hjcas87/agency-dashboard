'use client'

import { useMemo, useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { IconArrowLeft, IconLoader2, IconPlus, IconReceipt, IconTrash } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from '@/components/core/ui/field'
import { Input } from '@/components/core/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/core/ui/select'

import type { ClientRecord } from '@/app/actions/custom/clients'
import { issueInvoiceManualAction } from '@/app/actions/custom/invoices'

const CONCEPT_OPTIONS: { value: '1' | '2' | '3'; label: string }[] = [
  { value: '1', label: 'Productos' },
  { value: '2', label: 'Servicios' },
  { value: '3', label: 'Productos y servicios' },
]

interface LineItemDraft {
  name: string
  amount: string
}

const EMPTY_LINE: LineItemDraft = { name: '', amount: '' }

interface ManualInvoiceFormProps {
  clients: ClientRecord[]
}

export function ManualInvoiceForm({ clients }: ManualInvoiceFormProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [clientId, setClientId] = useState<string>('')
  const [issueDate, setIssueDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [concept, setConcept] = useState<'1' | '2' | '3'>('1')
  const [serviceFrom, setServiceFrom] = useState('')
  const [serviceTo, setServiceTo] = useState('')
  const [reference, setReference] = useState('')
  const [lines, setLines] = useState<LineItemDraft[]>([{ ...EMPTY_LINE }])

  const requiresServiceDates = concept === '2' || concept === '3'

  const total = useMemo(
    () =>
      lines.reduce((sum, line) => {
        const value = parseFloat(line.amount)
        return sum + (Number.isFinite(value) ? value : 0)
      }, 0),
    [lines]
  )

  function addLine() {
    setLines(prev => [...prev, { ...EMPTY_LINE }])
  }

  function removeLine(index: number) {
    setLines(prev => (prev.length === 1 ? prev : prev.filter((_, i) => i !== index)))
  }

  function updateLine(index: number, key: keyof LineItemDraft, value: string) {
    setLines(prev => prev.map((line, i) => (i === index ? { ...line, [key]: value } : line)))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!clientId) {
      toast.error('Elegí un cliente.')
      return
    }
    const cleanedLines = lines
      .map(line => ({ name: line.name.trim(), amount: line.amount.trim() }))
      .filter(line => line.name && parseFloat(line.amount) > 0)
    if (cleanedLines.length === 0) {
      toast.error('Agregá al menos una línea con nombre y monto válidos.')
      return
    }

    startTransition(async () => {
      const result = await issueInvoiceManualAction({
        client_id: parseInt(clientId, 10),
        issue_date: issueDate,
        concept: parseInt(concept, 10) as 1 | 2 | 3,
        service_date_from: requiresServiceDates ? serviceFrom : undefined,
        service_date_to: requiresServiceDates ? serviceTo : undefined,
        line_items: cleanedLines,
        commercial_reference: reference || undefined,
      })
      if (result.success) {
        toast.success(
          `Factura C N°${result.data.receipt_number ?? '?'} emitida — CAE ${result.data.cae ?? '—'}`
        )
        router.push(`/invoices/${result.data.id}`)
        router.refresh()
      } else {
        toast.error(result.error)
      }
    })
  }

  return (
    <div className="flex w-full flex-col gap-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <a href="/invoices">
            <IconArrowLeft data-icon="inline-start" />
            <span className="sr-only">Volver a facturación</span>
          </a>
        </Button>
        <h1 className="text-lg font-semibold">Nueva factura manual</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Factura C</CardTitle>
          <CardDescription>
            Emití una Factura C contra AFIP sin partir de un presupuesto.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            <FieldGroup className="grid gap-4 md:grid-cols-2">
              <Field>
                <FieldLabel htmlFor="client">
                  Cliente <span className="text-destructive">*</span>
                </FieldLabel>
                <Select value={clientId} onValueChange={setClientId} disabled={isPending}>
                  <SelectTrigger id="client">
                    <SelectValue placeholder="Elegí un cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.length === 0 ? (
                      <SelectItem value="__none__" disabled>
                        No hay clientes cargados
                      </SelectItem>
                    ) : (
                      clients.map(c => (
                        <SelectItem key={c.id} value={c.id.toString()}>
                          {c.name}
                          {c.company ? ` — ${c.company}` : ''}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
                <FieldDescription>
                  Si no tiene CUIT cargado se factura como Consumidor Final.
                </FieldDescription>
              </Field>

              <Field>
                <FieldLabel htmlFor="issue-date">
                  Fecha de emisión <span className="text-destructive">*</span>
                </FieldLabel>
                <Input
                  id="issue-date"
                  type="date"
                  value={issueDate}
                  onChange={e => setIssueDate(e.target.value)}
                  disabled={isPending}
                  required
                />
              </Field>

              <Field>
                <FieldLabel htmlFor="concept">Concepto</FieldLabel>
                <Select
                  value={concept}
                  onValueChange={value => setConcept(value as '1' | '2' | '3')}
                  disabled={isPending}
                >
                  <SelectTrigger id="concept">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CONCEPT_OPTIONS.map(option => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>

              <Field>
                <FieldLabel htmlFor="reference">Referencia comercial</FieldLabel>
                <Input
                  id="reference"
                  value={reference}
                  onChange={e => setReference(e.target.value)}
                  maxLength={50}
                  placeholder="Opcional"
                  disabled={isPending}
                />
              </Field>

              {requiresServiceDates && (
                <>
                  <Field>
                    <FieldLabel htmlFor="service-from">
                      Servicio desde <span className="text-destructive">*</span>
                    </FieldLabel>
                    <Input
                      id="service-from"
                      type="date"
                      value={serviceFrom}
                      onChange={e => setServiceFrom(e.target.value)}
                      disabled={isPending}
                      required
                    />
                  </Field>
                  <Field>
                    <FieldLabel htmlFor="service-to">
                      Servicio hasta <span className="text-destructive">*</span>
                    </FieldLabel>
                    <Input
                      id="service-to"
                      type="date"
                      value={serviceTo}
                      onChange={e => setServiceTo(e.target.value)}
                      disabled={isPending}
                      required
                    />
                  </Field>
                </>
              )}
            </FieldGroup>

            <FieldSet>
              <FieldLegend>Detalle</FieldLegend>
              <FieldDescription>
                Agregá las líneas que entran en la factura. El total se calcula automáticamente.
              </FieldDescription>
              <div className="flex flex-col gap-3">
                {lines.map((line, index) => (
                  <div key={index} className="grid grid-cols-1 gap-2 md:grid-cols-[1fr_180px_auto]">
                    <Input
                      placeholder="Descripción de la línea"
                      value={line.name}
                      onChange={e => updateLine(index, 'name', e.target.value)}
                      disabled={isPending}
                    />
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="Monto ARS"
                      value={line.amount}
                      onChange={e => updateLine(index, 'amount', e.target.value)}
                      disabled={isPending}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeLine(index)}
                      disabled={isPending || lines.length === 1}
                    >
                      <IconTrash data-icon="inline-start" />
                      <span className="sr-only">Quitar línea</span>
                    </Button>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addLine}
                  disabled={isPending}
                  className="self-start"
                >
                  <IconPlus data-icon="inline-start" />
                  Agregar línea
                </Button>
              </div>
              <div className="flex items-center justify-end gap-3 border-t pt-3 text-sm">
                <span className="text-muted-foreground">Total ARS</span>
                <span className="font-semibold">
                  {total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}
                </span>
              </div>
            </FieldSet>

            <div className="flex items-center justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.push('/invoices')}
                disabled={isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isPending || total <= 0}>
                {isPending ? (
                  <IconLoader2 className="animate-spin" data-icon="inline-start" />
                ) : (
                  <IconReceipt data-icon="inline-start" />
                )}
                {isPending ? 'Emitiendo…' : 'Emitir factura'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
