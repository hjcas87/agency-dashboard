'use client'

import { useId } from 'react'
import { IconPlus, IconTrash } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import { Field, FieldGroup, FieldLabel, FieldLegend, FieldSet } from '@/components/core/ui/field'
import { Input } from '@/components/core/ui/input'

export interface AdditionalEmailDraft {
  email: string
  label: string
}

interface AdditionalEmailsSectionProps {
  values: AdditionalEmailDraft[]
  onChange: (next: AdditionalEmailDraft[]) => void
  disabled?: boolean
}

/**
 * Repeating "label + email" inputs for a client's CC recipients.
 *
 * The primary email is captured separately on the form. Each row here
 * is a co-recipient who must always be CC'd when reaching out — typical
 * cases: tesorería / administración / secretaría sharing the contact.
 *
 * The list is shipped to the backend as a JSON-stringified hidden
 * input; the Action's `buildClientBody` parses it back into the
 * `additional_emails` payload.
 */
export function AdditionalEmailsSection({
  values,
  onChange,
  disabled,
}: AdditionalEmailsSectionProps) {
  const baseId = useId()

  function update(index: number, patch: Partial<AdditionalEmailDraft>) {
    onChange(values.map((row, i) => (i === index ? { ...row, ...patch } : row)))
  }

  function add() {
    onChange([...values, { email: '', label: '' }])
  }

  function remove(index: number) {
    onChange(values.filter((_, i) => i !== index))
  }

  return (
    <FieldSet className="gap-3">
      <FieldLegend>Emails adicionales (CC)</FieldLegend>
      <p className="text-sm text-muted-foreground">
        Estos correos se agregan como CC cuando se envía un presupuesto o factura al cliente.
        Útil para sumar tesorería, administración o cualquier otro destinatario fijo.
      </p>

      {values.length === 0 ? (
        <p className="text-xs text-muted-foreground italic">
          Sin emails adicionales. Sumá uno con el botón de abajo si hace falta.
        </p>
      ) : (
        <FieldGroup className="gap-3">
          {values.map((row, index) => (
            <div
              key={`${baseId}-${index}`}
              className="grid gap-2 md:grid-cols-[1fr_2fr_auto]"
            >
              <Field>
                <FieldLabel htmlFor={`${baseId}-label-${index}`} className="text-xs">
                  Etiqueta
                </FieldLabel>
                <Input
                  id={`${baseId}-label-${index}`}
                  placeholder="Tesorería"
                  value={row.label}
                  onChange={e => update(index, { label: e.target.value })}
                  disabled={disabled}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor={`${baseId}-email-${index}`} className="text-xs">
                  Email
                </FieldLabel>
                <Input
                  id={`${baseId}-email-${index}`}
                  type="email"
                  placeholder="tesoreria@ejemplo.com"
                  value={row.email}
                  onChange={e => update(index, { email: e.target.value })}
                  disabled={disabled}
                />
              </Field>
              <div className="flex items-end pb-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => remove(index)}
                  disabled={disabled}
                  aria-label="Quitar email"
                >
                  <IconTrash className="size-4 text-destructive" />
                </Button>
              </div>
            </div>
          ))}
        </FieldGroup>
      )}

      <div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={add}
          disabled={disabled}
        >
          <IconPlus data-icon="inline-start" />
          Sumar email
        </Button>
      </div>

      <input
        type="hidden"
        name="additional_emails"
        value={JSON.stringify(
          values
            .map(r => ({ email: r.email.trim(), label: r.label.trim() }))
            .filter(r => r.email.length > 0)
        )}
      />
    </FieldSet>
  )
}
