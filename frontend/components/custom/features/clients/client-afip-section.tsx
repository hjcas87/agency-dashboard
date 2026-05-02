'use client'

import { useTransition } from 'react'
import { toast } from 'sonner'
import { IconLoader2, IconSearch } from '@tabler/icons-react'

import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from '@/components/core/ui/field'
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from '@/components/core/ui/input-group'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/core/ui/select'

import {
  lookupCuitInAfipAction,
  type CuitLookupResult,
  type IvaCondition,
} from '@/app/actions/custom/clients'

// Mirror of IvaCondition labels from
// backend/app/shared/afip/messages.py — operator-facing strings only.
export const IVA_CONDITION_LABELS: Record<IvaCondition, string> = {
  RI: 'Responsable Inscripto',
  MT: 'Monotributista',
  EX: 'IVA Exento',
  NA: 'IVA No Alcanzado',
  CF: 'Consumidor Final',
  NC: 'No Categorizado',
}

const IVA_CONDITION_ORDER: IvaCondition[] = ['RI', 'MT', 'EX', 'NA', 'CF', 'NC']

// Sentinel value the Select uses to represent "no IVA condition picked".
const IVA_UNSET = '__unset__'

export interface ClientAfipFields {
  cuit: string
  ivaCondition: IvaCondition | null
}

interface ClientAfipSectionProps {
  values: ClientAfipFields
  onChange: (next: ClientAfipFields) => void
  /**
   * Called when the AFIP lookup succeeds. The form decides how to apply
   * the suggestions — typically "fill empty fields, don't overwrite
   * what the user already typed". This component just hands the data
   * upstream.
   */
  onAfipAutofill?: (result: CuitLookupResult) => void
  disabled?: boolean
}

export function ClientAfipSection({
  values,
  onChange,
  onAfipAutofill,
  disabled = false,
}: ClientAfipSectionProps) {
  const [isLooking, startLookup] = useTransition()

  const normalizedCuit = values.cuit.replace(/[-\s]/g, '')
  const canLookup = /^\d{11}$/.test(normalizedCuit)

  function handleLookup() {
    startLookup(async () => {
      const result = await lookupCuitInAfipAction(normalizedCuit)
      if (!result.success) {
        toast.error(result.error)
        return
      }
      onChange({
        cuit: normalizedCuit,
        ivaCondition: values.ivaCondition ?? result.data.iva_condition,
      })
      onAfipAutofill?.(result.data)
      const status = result.data.status ? ` (${result.data.status})` : ''
      toast.success(`Padrón AFIP consultado${status}`)
    })
  }

  return (
    <FieldSet>
      <FieldLegend>Datos AFIP</FieldLegend>
      <FieldDescription>
        Opcional. Completá el CUIT y usá &quot;Buscar en AFIP&quot; para autocompletar razón social
        y condición IVA.
      </FieldDescription>
      <FieldGroup className="grid gap-4 md:grid-cols-2">
        <Field>
          <FieldLabel htmlFor="cuit">CUIT</FieldLabel>
          <InputGroup>
            <InputGroupInput
              id="cuit"
              name="cuit"
              value={values.cuit}
              onChange={e => onChange({ ...values, cuit: e.target.value })}
              placeholder="20-12345678-9"
              maxLength={13}
              disabled={disabled || isLooking}
            />
            <InputGroupAddon align="inline-end">
              <InputGroupButton
                type="button"
                size="xs"
                onClick={handleLookup}
                disabled={disabled || isLooking || !canLookup}
              >
                {isLooking ? <IconLoader2 className="animate-spin" /> : <IconSearch />}
                Buscar en AFIP
              </InputGroupButton>
            </InputGroupAddon>
          </InputGroup>
        </Field>

        <Field>
          <FieldLabel htmlFor="iva_condition">Condición frente al IVA</FieldLabel>
          <Select
            value={values.ivaCondition ?? IVA_UNSET}
            onValueChange={value =>
              onChange({
                ...values,
                ivaCondition: value === IVA_UNSET ? null : (value as IvaCondition),
              })
            }
            disabled={disabled || isLooking}
          >
            <SelectTrigger id="iva_condition">
              <SelectValue placeholder="Sin especificar" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={IVA_UNSET}>Sin especificar</SelectItem>
              {IVA_CONDITION_ORDER.map(code => (
                <SelectItem key={code} value={code}>
                  {IVA_CONDITION_LABELS[code]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <input type="hidden" name="iva_condition" value={values.ivaCondition ?? ''} readOnly />
        </Field>
      </FieldGroup>
    </FieldSet>
  )
}
