'use client'

import { useRouter } from 'next/navigation'
import { useState, useTransition } from 'react'
import { toast } from 'sonner'
import { IconArrowLeft, IconDeviceFloppy } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import { Field, FieldGroup, FieldLabel } from '@/components/core/ui/field'
import { Input } from '@/components/core/ui/input'
import { Separator } from '@/components/core/ui/separator'

import { createClientAction, type CuitLookupResult } from '@/app/actions/custom/clients'
import {
  ClientAfipSection,
  type ClientAfipFields,
} from '@/components/custom/features/clients/client-afip-section'
import { CLIENT_MESSAGES } from '@/lib/messages'

interface ClientCoreFields {
  name: string
  company: string
  email: string
  phone: string
}

const EMPTY_CORE: ClientCoreFields = { name: '', company: '', email: '', phone: '' }
const EMPTY_AFIP: ClientAfipFields = { cuit: '', ivaCondition: null }

function applyAfipAutofill(
  core: ClientCoreFields,
  afip: ClientAfipFields,
  result: CuitLookupResult
): { core: ClientCoreFields; afip: ClientAfipFields } {
  // Don't overwrite anything the operator already typed.
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

export function ClientForm() {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [formError, setFormError] = useState<string | null>(null)
  const [core, setCore] = useState<ClientCoreFields>(EMPTY_CORE)
  const [afip, setAfip] = useState<ClientAfipFields>(EMPTY_AFIP)

  function handleSubmit(formData: FormData) {
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
            {isPending ? 'Guardando...' : 'Guardar Cliente'}
          </Button>
        </div>
      </form>
    </div>
  )
}
