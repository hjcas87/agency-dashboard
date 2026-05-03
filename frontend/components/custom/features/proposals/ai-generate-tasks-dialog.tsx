'use client'

import { IconCheck, IconCopy, IconLoader2, IconSparkles } from '@tabler/icons-react'
import { useEffect, useState } from 'react'
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
import { Label } from '@/components/core/ui/label'
import { Textarea } from '@/components/core/ui/textarea'

import { PROPOSAL_MESSAGES } from '@/lib/messages'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const M = PROPOSAL_MESSAGES.aiGenerate

export interface AIParsedTask {
  name: string
  description: string | null
  hours: string
}

export interface AIParsedResult {
  deliverables_summary: string | null
  tasks: AIParsedTask[]
}

interface AIGenerateTasksDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onResult: (result: AIParsedResult) => void
}

export function AIGenerateTasksDialog({
  open,
  onOpenChange,
  onResult,
}: AIGenerateTasksDialogProps) {
  const [raw, setRaw] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!open) return
    setRaw('')
    setError(null)
    setCopied(false)
  }, [open])

  async function handleCopyPrompt() {
    try {
      await navigator.clipboard.writeText(M.promptTemplate)
      setCopied(true)
      toast.success(M.copyDone)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error(M.genericError)
    }
  }

  async function handleApply() {
    setError(null)
    if (!raw.trim()) {
      setError(M.emptyError)
      return
    }
    setSubmitting(true)
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/parse-ai-input`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw }),
      })
      if (!res.ok) {
        const payload = await res.json().catch(() => ({ detail: M.genericError }))
        const detail = typeof payload.detail === 'string' ? payload.detail : M.genericError
        setError(detail)
        return
      }
      const data = (await res.json()) as {
        deliverables_summary: string | null
        tasks: { name: string; description: string | null; hours: number | string }[]
      }
      onResult({
        deliverables_summary: data.deliverables_summary ?? null,
        tasks: data.tasks.map(t => ({
          name: t.name,
          description: t.description ?? null,
          hours: String(t.hours),
        })),
      })
      toast.success(M.successToast)
      onOpenChange(false)
    } catch {
      setError(M.genericError)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[90vh] w-[95vw] max-w-[95vw] flex-col sm:max-w-[95vw] lg:max-w-300">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <IconSparkles className="size-5 text-emerald-600" />
            {M.dialogTitle}
          </DialogTitle>
          <DialogDescription>{M.dialogDescription}</DialogDescription>
        </DialogHeader>

        <div className="flex flex-1 flex-col gap-5 overflow-y-auto">
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-semibold">{M.promptHeading}</Label>
              <Button type="button" size="sm" variant="outline" onClick={handleCopyPrompt}>
                {copied ? (
                  <IconCheck className="size-4" data-icon="inline-start" />
                ) : (
                  <IconCopy className="size-4" data-icon="inline-start" />
                )}
                {copied ? M.copyDone : M.copyButton}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">{M.promptHelper}</p>
            <Textarea
              readOnly
              value={M.promptTemplate}
              rows={6}
              className="h-40 resize-y text-xs field-sizing-fixed"
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="ai-json" className="text-sm font-semibold">
              {M.pasteHeading}
            </Label>
            <Textarea
              id="ai-json"
              value={raw}
              onChange={e => setRaw(e.target.value)}
              placeholder={M.pastePlaceholder}
              rows={10}
              className="h-56 resize-y text-xs field-sizing-fixed"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive whitespace-pre-line">
              {error}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={submitting}
          >
            {M.cancelButton}
          </Button>
          <Button type="button" onClick={handleApply} disabled={submitting}>
            {submitting ? (
              <>
                <IconLoader2 className="size-4 animate-spin" data-icon="inline-start" />
                {M.applyingButton}
              </>
            ) : (
              <>
                <IconSparkles className="size-4" data-icon="inline-start" />
                {M.applyButton}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
