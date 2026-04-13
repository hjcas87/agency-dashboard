'use client'

import { useRouter } from 'next/navigation'
import { useState, useTransition } from 'react'
import { toast } from 'sonner'
import { IconArrowLeft, IconDeviceFloppy } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import { Input } from '@/components/core/ui/input'
import { Label } from '@/components/core/ui/label'
import { Separator } from '@/components/core/ui/separator'
import { CLIENT_MESSAGES } from '@/lib/messages'
import { createClientAction } from '@/app/actions/custom/clients'

export function ClientForm() {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [formError, setFormError] = useState<string | null>(null)

  async function handleSubmit(formData: FormData) {
    setFormError(null)
    startTransition(async () => {
      const result = await createClientAction(formData)
      if (result.success) {
        toast.success(CLIENT_MESSAGES.createSuccess.title, {
          description: CLIENT_MESSAGES.createSuccess.description,
        })
        router.push('/clients')
        router.refresh()
      } else {
        setFormError(result.error)
        toast.error(CLIENT_MESSAGES.createError.title, {
          description: result.error,
        })
      }
    })
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <a href="/clients">
            <IconArrowLeft className="size-4" />
          </a>
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Crear Cliente</h1>
          <p className="text-sm text-muted-foreground">
            Completá los datos para registrar un nuevo cliente.
          </p>
        </div>
      </div>

      <Separator />

      {/* Form */}
      <form action={handleSubmit} className="flex flex-col gap-6">
        <div className="flex flex-col gap-4">
          {/* Name */}
          <div className="flex flex-col gap-2">
            <Label htmlFor="name">
              Nombre <span className="text-destructive">*</span>
            </Label>
            <Input id="name" name="name" placeholder="Nombre del cliente" required disabled={isPending} />
          </div>

          {/* Company */}
          <div className="flex flex-col gap-2">
            <Label htmlFor="company">Empresa</Label>
            <Input id="company" name="company" placeholder="Nombre de la empresa (opcional)" disabled={isPending} />
          </div>

          {/* Email */}
          <div className="flex flex-col gap-2">
            <Label htmlFor="email">
              Email <span className="text-destructive">*</span>
            </Label>
            <Input id="email" name="email" type="email" placeholder="cliente@email.com" required disabled={isPending} />
          </div>

          {/* Phone */}
          <div className="flex flex-col gap-2">
            <Label htmlFor="phone">Teléfono</Label>
            <Input id="phone" name="phone" type="tel" placeholder="+54 11 1234-5678" disabled={isPending} />
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
          <Button variant="outline" type="button" onClick={() => router.push('/clients')} disabled={isPending}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isPending}>
            <IconDeviceFloppy className="size-4" />
            {isPending ? 'Guardando...' : 'Guardar Cliente'}
          </Button>
        </div>
      </form>
    </div>
  )
}
