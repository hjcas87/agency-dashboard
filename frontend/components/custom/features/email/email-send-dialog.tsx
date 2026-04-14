"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { IconMail, IconX, IconLoader2 } from "@tabler/icons-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/core/ui/dialog";
import { Button } from "@/components/core/ui/button";
import { Label } from "@/components/core/ui/label";
import { Input } from "@/components/core/ui/input";
import { Textarea } from "@/components/core/ui/textarea";
import { Checkbox } from "@/components/core/ui/checkbox";
import { Separator } from "@/components/core/ui/separator";

import { EmailSendRequest } from "@/lib/shared/email/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface EmailSendDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  recipient?: string;
  subject?: string;
  proposalId?: number;
  clientId?: number | null;
}

export function EmailSendDialog({
  open,
  onOpenChange,
  recipient: initialRecipient = "",
  subject = "",
  proposalId,
  clientId,
}: EmailSendDialogProps) {
  const [to, setTo] = useState(initialRecipient);
  const [emailSubject, setEmailSubject] = useState(subject);
  const [body, setBody] = useState("");
  const [attachPdf, setAttachPdf] = useState(!!proposalId);
  const [sending, setSending] = useState(false);
  const [loadingClient, setLoadingClient] = useState(false);

  const loadClientEmail = useCallback(async () => {
    if (!clientId || to) return;
    setLoadingClient(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/clients/${clientId}`);
      if (res.ok) {
        const client = await res.json();
        if (client.email) {
          setTo(client.email);
        }
      }
    } catch {
      // Silently fail — user can type manually
    } finally {
      setLoadingClient(false);
    }
  }, [clientId, to]);

  useEffect(() => {
    if (open) {
      setTo(initialRecipient);
      setEmailSubject(subject);
      setAttachPdf(!!proposalId);
      if (clientId && !initialRecipient) {
        void loadClientEmail();
      }
    }
  }, [open, initialRecipient, subject, proposalId, clientId, loadClientEmail]);

  async function handleSend() {
    if (!to || !emailSubject || !body) {
      toast.error("Por favor completa todos los campos obligatorios");
      return;
    }

    setSending(true);
    try {
      const request: EmailSendRequest = {
        to,
        subject: emailSubject,
        body,
        attach_proposal_pdf: attachPdf && proposalId ? proposalId : undefined,
      };

      const endpoint = proposalId
        ? `/api/v1/email/proposals/${proposalId}/send`
        : "/api/v1/email/send";

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });

      if (res.ok) {
        toast.success("Email enviado exitosamente");
        onOpenChange(false);
      } else {
        const error = await res.json().catch(() => ({ detail: "Error al enviar el email" }));
        toast.error(error.detail || "Error al enviar el email");
      }
    } catch (error) {
      toast.error("Error al enviar el email");
    } finally {
      setSending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Enviar Email</DialogTitle>
          <DialogDescription>
            Envía un email con el PDF adjunto al cliente
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label>Para</Label>
            <Input
              type="email"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="cliente@ejemplo.com"
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label>Asunto</Label>
            <Input
              value={emailSubject}
              onChange={(e) => setEmailSubject(e.target.value)}
              placeholder="Asunto del email"
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label>Cuerpo del Email</Label>
            <Textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
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
                  onCheckedChange={(checked) => setAttachPdf(!!checked)}
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
  );
}
