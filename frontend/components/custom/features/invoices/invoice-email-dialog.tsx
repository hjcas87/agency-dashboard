'use client'

import { useEffect, useState, useTransition } from 'react'
import { toast } from 'sonner'
import { IconLoader2, IconMail } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/core/ui/dialog'
import { Field, FieldGroup, FieldLabel } from '@/components/core/ui/field'
import { Input } from '@/components/core/ui/input'
import { Textarea } from '@/components/core/ui/textarea'

import type { InvoiceRecord } from '@/app/actions/custom/invoices'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface InvoiceEmailDialogProps {
  invoice: InvoiceRecord | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function InvoiceEmailDialog({ invoice, open, onOpenChange }: InvoiceEmailDialogProps) {
  const [isPending, startTransition] = useTransition()
  const [to, setTo] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')

  // Reset fields whenever the dialog opens with a new invoice. Same pattern
  // as the email-send-dialog fix in commit 63454b4 — never put `to` (etc.)
  // in the deps, so user typing does not trigger a reset loop.
  useEffect(() => {
    if (!open || !invoice) return
    const isInternal = invoice.is_internal
    const docLabel = isInternal ? 'presupuesto' : 'factura'
    const docNumber = isInternal
      ? invoice.internal_number
        ? `N°${String(invoice.internal_number).padStart(8, '0')}`
        : ''
      : invoice.receipt_number
        ? `N°${invoice.receipt_number}`
        : ''
    const titleCase = isInternal ? 'Presupuesto' : 'Factura'
    setSubject(`${titleCase} ${docNumber}`.trim())
    setBody(
      `Hola${invoice.client_name ? ` ${invoice.client_name}` : ''},\n\n` +
        `Te adjunto el ${docLabel} ${docNumber}.\n\nSaludos.`
    )
  }, [open, invoice])

  // Pre-fill recipient from the client's email — fetched from the backend.
  // Independent effect, no dependency on `to` to avoid the reset loop.
  useEffect(() => {
    if (!open || !invoice) return
    let cancelled = false
    ;(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/clients/${invoice.client_id}`)
        if (cancelled || !res.ok) return
        const client = await res.json()
        if (client.email) setTo(client.email)
      } catch {
        // Silent — operator types manually
      }
    })()
    return () => {
      cancelled = true
    }
  }, [open, invoice])

  function handleSend() {
    if (!invoice) return
    if (!to || !subject || !body) {
      toast.error('Completá destinatario, asunto y mensaje.')
      return
    }
    startTransition(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/email/invoices/${invoice.id}/send`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ to, subject, body }),
        })
        if (res.ok) {
          toast.success('Email enviado')
          onOpenChange(false)
        } else {
          const data = await res.json().catch(() => ({}))
          toast.error((data.detail as string) || 'Error al enviar el email')
        }
      } catch {
        toast.error('Error de conexión con el servidor')
      }
    })
  }

  const isInternal = invoice?.is_internal ?? false
  const docNoun = isInternal ? 'presupuesto' : 'factura'

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Enviar {docNoun} por email</DialogTitle>
          <DialogDescription>
            {isInternal
              ? 'El presupuesto se envía con el PDF adjunto al destinatario. Recordá que es un comprobante interno sin validez fiscal.'
              : 'La factura se envía con el PDF adjunto al destinatario.'}
          </DialogDescription>
        </DialogHeader>

        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="email-to">Para</FieldLabel>
            <Input
              id="email-to"
              type="email"
              value={to}
              onChange={e => setTo(e.target.value)}
              placeholder="cliente@ejemplo.com"
              disabled={isPending}
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="email-subject">Asunto</FieldLabel>
            <Input
              id="email-subject"
              value={subject}
              onChange={e => setSubject(e.target.value)}
              disabled={isPending}
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="email-body">Mensaje</FieldLabel>
            <Textarea
              id="email-body"
              value={body}
              onChange={e => setBody(e.target.value)}
              rows={6}
              disabled={isPending}
            />
          </Field>
        </FieldGroup>

        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)} disabled={isPending}>
            Cancelar
          </Button>
          <Button onClick={handleSend} disabled={isPending}>
            {isPending ? (
              <IconLoader2 className="animate-spin" data-icon="inline-start" />
            ) : (
              <IconMail data-icon="inline-start" />
            )}
            {isPending ? 'Enviando…' : 'Enviar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
