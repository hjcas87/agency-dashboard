'use client'

import { useRouter } from 'next/navigation'
import { useState, useTransition } from 'react'
import { toast } from 'sonner'
import { IconArrowLeft, IconDeviceFloppy } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import { Field, FieldGroup, FieldLabel } from '@/components/core/ui/field'
import { Input } from '@/components/core/ui/input'
import { Separator } from '@/components/core/ui/separator'

import {
  updateClientAction,
  type CuitLookupResult,
  type IvaCondition,
} from '@/app/actions/custom/clients'
import {
  ClientAfipSection,
  type ClientAfipFields,
} from '@/components/custom/features/clients/client-afip-section'
import { CLIENT_MESSAGES } from '@/lib/messages'

interface ClientEditFormProps {
  client: {
    id: number
    name: string
    company: string | null
    email: string
    phone: string | null
    cuit: string | null
    iva_condition: IvaCondition | null
  }
}

interface ClientCoreFields {
  name: string
  company: string
  email: string
  phone: string
}

function applyAfipAutofill(
  core: ClientCoreFields,
  afip: ClientAfipFields,
  result: CuitLookupResult
): { core: ClientCoreFields; afip: ClientAfipFields } {
  const composedName = [result.first_name, result.last_name].filter(Boolean).join(' ').trim() || ''
  return {
    core: {
      name: core.name || composedName,
      company: core.company || result.company_name || '',
      email: core.email,
      phone: core.phone,
    },
    afip: {
      cuit: result.cuit,
      ivaCondition: afip.ivaCondition ?? result.iva_condition,
    },
  }
}

export function ClientEditForm({ client }: ClientEditFormProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [formError, setFormError] = useState<string | null>(null)
  const [core, setCore] = useState<ClientCoreFields>({
    name: client.name,
    company: client.company ?? '',
    email: client.email,
    phone: client.phone ?? '',
  })
  const [afip, setAfip] = useState<ClientAfipFields>({
    cuit: client.cuit ?? '',
    ivaCondition: client.iva_condition,
  })

  function handleSubmit(formData: FormData) {
    setFormError(null)
    startTransition(async () => {
      const result = await updateClientAction(client.id, formData)
      if (result.success) {
        toast.success(CLIENT_MESSAGES.updateSuccess.title, {
          description: CLIENT_MESSAGES.updateSuccess.description,
        })
        router.push('/clients')
        router.refresh()
      } else {
        setFormError(result.error)
        toast.error(CLIENT_MESSAGES.updateError.title, {
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
          <h1 className="text-2xl font-bold">Editar Cliente</h1>
          <p className="text-sm text-muted-foreground">
            Modificá los datos de <span className="font-medium">{client.name}</span>.
          </p>
        </div>
      </div>

      <Separator />

      <form action={handleSubmit} className="flex flex-col gap-6">
        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="name">
              Nombre <span className="text-destructive">*</span>
            </FieldLabel>
            <Input
              id="name"
              name="name"
              placeholder="Nombre del cliente"
              required
              disabled={isPending}
              value={core.name}
              onChange={e => setCore(prev => ({ ...prev, name: e.target.value }))}
            />
          </Field>

          <Field>
            <FieldLabel htmlFor="company">Empresa</FieldLabel>
            <Input
              id="company"
              name="company"
              placeholder="Nombre de la empresa (opcional)"
              disabled={isPending}
              value={core.company}
              onChange={e => setCore(prev => ({ ...prev, company: e.target.value }))}
            />
          </Field>

          <Field>
            <FieldLabel htmlFor="email">
              Email <span className="text-destructive">*</span>
            </FieldLabel>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="cliente@email.com"
              required
              disabled={isPending}
              value={core.email}
              onChange={e => setCore(prev => ({ ...prev, email: e.target.value }))}
            />
          </Field>

          <Field>
            <FieldLabel htmlFor="phone">Teléfono</FieldLabel>
            <Input
              id="phone"
              name="phone"
              type="tel"
              placeholder="+54 11 1234-5678"
              disabled={isPending}
              value={core.phone}
              onChange={e => setCore(prev => ({ ...prev, phone: e.target.value }))}
            />
          </Field>
        </FieldGroup>

        <ClientAfipSection
          values={afip}
          onChange={setAfip}
          onAfipAutofill={result => {
            const next = applyAfipAutofill(core, afip, result)
            setCore(next.core)
            setAfip(next.afip)
          }}
          disabled={isPending}
        />

        {formError && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            {formError}
          </div>
        )}

        <div className="flex items-center justify-end gap-3">
          <Button
            variant="outline"
            type="button"
            onClick={() => router.push('/clients')}
            disabled={isPending}
          >
            Cancelar
          </Button>
          <Button type="submit" disabled={isPending}>
            <IconDeviceFloppy className="size-4" />
            {isPending ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        </div>
      </form>
    </div>
  )
}
