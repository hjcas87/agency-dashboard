'use client'

import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { IconMail, IconX, IconLoader2 } from '@tabler/icons-react'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/core/ui/dialog'
import { Button } from '@/components/core/ui/button'
import { Label } from '@/components/core/ui/label'
import { Input } from '@/components/core/ui/input'
import { Textarea } from '@/components/core/ui/textarea'
import { Checkbox } from '@/components/core/ui/checkbox'
import { Separator } from '@/components/core/ui/separator'

import { EmailSendRequest } from '@/lib/shared/email/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AvailableEmail {
  email: string
  label: string
  is_primary: boolean
}

interface EmailSendDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  recipient?: string
  subject?: string
  proposalId?: number
  clientId?: number | null
}

export function EmailSendDialog({
  open,
  onOpenChange,
  recipient: initialRecipient = '',
  subject = '',
  proposalId,
  clientId,
}: EmailSendDialogProps) {
  const [to, setTo] = useState(initialRecipient)
  const [emailSubject, setEmailSubject] = useState(subject)
  const [body, setBody] = useState('')
  const [attachPdf, setAttachPdf] = useState(!!proposalId)
  const [sending, setSending] = useState(false)
  const [availableEmails, setAvailableEmails] = useState<AvailableEmail[]>([])
  const [selectedEmails, setSelectedEmails] = useState<Set<string>>(new Set())
  const [ccFixed, setCcFixed] = useState<string[]>([])

  // Reset the form to the props when the dialog opens. Runs only on
  // open / props change — never on each keystroke.
  useEffect(() => {
    if (!open) return
    setTo(initialRecipient)
    setEmailSubject(subject)
    setBody('')
    setAttachPdf(!!proposalId)
    setAvailableEmails([])
    setSelectedEmails(new Set())
    setCcFixed([])
  }, [open, initialRecipient, subject, proposalId])

  // When the dialog opens for a specific proposal, fetch the full
  // template payload (subject + body + recipient choices + fixed CC)
  // and pre-fill. The operator can still tweak before sending.
  useEffect(() => {
    if (!open || !proposalId) return
    let cancelled = false
    ;(async () => {
      try {
        const res = await fetch(
          `${API_BASE}/api/v1/email/proposals/${proposalId}/template`
        )
        if (cancelled || !res.ok) return
        const template = await res.json() as {
          to: string
          subject: string
          body: string
          available_emails: AvailableEmail[]
          cc_fixed: string[]
        }
        if (template.subject) setEmailSubject(template.subject)
        if (template.body) setBody(template.body)
        setAvailableEmails(template.available_emails ?? [])
        setCcFixed(template.cc_fixed ?? [])
        // Pre-select primary email(s); fall back to template.to if no
        // primary flag was provided.
        const primaries = (template.available_emails ?? [])
          .filter(e => e.is_primary)
          .map(e => e.email)
        if (primaries.length > 0) {
          setSelectedEmails(new Set(primaries))
        } else if (template.to) {
          setSelectedEmails(new Set([template.to]))
        }
        if (template.to) setTo(template.to)
      } catch {
        // Silently fail — operator types manually.
      }
    })()
    return () => {
      cancelled = true
    }
  }, [open, proposalId])

  // Fallback: pull email from the client when there's no proposalId
  // but a clientId is given (free-form mode).
  useEffect(() => {
    if (!open || proposalId || !clientId || initialRecipient) return
    let cancelled = false
    ;(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/clients/${clientId}`)
        if (cancelled || !res.ok) return
        const client = await res.json()
        if (client.email) setTo(client.email)
      } catch {
        // Silently fail.
      }
    })()
    return () => {
      cancelled = true
    }
  }, [open, proposalId, clientId, initialRecipient])

  function toggleSelected(email: string, checked: boolean) {
    setSelectedEmails(prev => {
      const next = new Set(prev)
      if (checked) {
        next.add(email)
      } else {
        next.delete(email)
      }
      return next
    })
  }

  async function handleSend() {
    // For proposal sends we drive recipients from the checkbox list;
    // for free-form sends we fall back to the single `to` input.
    const proposalMode = proposalId && availableEmails.length > 0
    const recipients = proposalMode
      ? availableEmails.map(e => e.email).filter(e => selectedEmails.has(e))
      : to.split(',').map(e => e.trim()).filter(Boolean)

    if (recipients.length === 0 || !emailSubject || !body) {
      toast.error('Necesitás al menos un destinatario, asunto y cuerpo')
      return
    }

    setSending(true)
    try {
      const request: EmailSendRequest = {
        to: recipients[0],
        cc: recipients.slice(1).join(', ') || undefined,
        subject: emailSubject,
        body,
        attach_proposal_pdf: attachPdf && proposalId ? proposalId : undefined,
      }

      const endpoint = proposalId
        ? `/api/v1/email/proposals/${proposalId}/send`
        : '/api/v1/email/send'

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      })

      if (res.ok) {
        toast.success('Email enviado exitosamente')
        onOpenChange(false)
      } else {
        const error = await res.json().catch(() => ({ detail: 'Error al enviar el email' }))
        toast.error(error.detail || 'Error al enviar el email')
      }
    } catch {
      toast.error('Error al enviar el email')
    } finally {
      setSending(false)
    }
  }

  const proposalMode = !!proposalId && availableEmails.length > 0

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Enviar Email</DialogTitle>
          <DialogDescription>Envía un email con el PDF adjunto al cliente</DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          {proposalMode ? (
            <div className="flex flex-col gap-2">
              <Label>Destinatarios</Label>
              <div className="flex flex-col gap-2 rounded-md border p-3">
                {availableEmails.map(option => {
                  const id = `recipient-${option.email}`
                  return (
                    <div key={option.email} className="flex items-center gap-3">
                      <Checkbox
                        id={id}
                        checked={selectedEmails.has(option.email)}
                        onCheckedChange={checked => toggleSelected(option.email, !!checked)}
                      />
                      <Label htmlFor={id} className="cursor-pointer text-sm font-normal">
                        <span className="font-medium">{option.label}</span>{' '}
                        <span className="text-muted-foreground">— {option.email}</span>
                      </Label>
                    </div>
                  )
                })}
              </div>
              {ccFixed.length > 0 && (
                <p className="text-xs text-muted-foreground">
                  También se envía con copia fija a:{' '}
                  <span className="font-mono">{ccFixed.join(', ')}</span>
                </p>
              )}
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <Label>Para</Label>
              <Input
                type="email"
                value={to}
                onChange={e => setTo(e.target.value)}
                placeholder="cliente@ejemplo.com (separá varios con comas)"
              />
            </div>
          )}

          <div className="flex flex-col gap-2">
            <Label>Asunto</Label>
            <Input
              value={emailSubject}
              onChange={e => setEmailSubject(e.target.value)}
              placeholder="Asunto del email"
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label>Cuerpo del Email</Label>
            <Textarea
              value={body}
              onChange={e => setBody(e.target.value)}
              placeholder="Estimado cliente..."
              rows={8}
            />
          </div>

          {proposalId && (
            <>
              <Separator />
              <div className="flex items-center gap-2">
                <Checkbox
                  id="attach-pdf"
                  checked={attachPdf}
                  onCheckedChange={checked => setAttachPdf(!!checked)}
                />
                <Label htmlFor="attach-pdf" className="text-sm">
                  Adjuntar PDF del presupuesto
                </Label>
              </div>
            </>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={sending}>
            <IconX className="size-4" data-icon="inline-start" />
            Cancelar
          </Button>
          <Button onClick={handleSend} disabled={sending}>
            {sending ? (
              <>
                <IconLoader2 className="size-4 animate-spin" data-icon="inline-start" />
                Enviando...
              </>
            ) : (
              <>
                <IconMail className="size-4" data-icon="inline-start" />
                Enviar
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
