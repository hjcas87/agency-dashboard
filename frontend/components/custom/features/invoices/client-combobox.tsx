'use client'

import { useMemo, useState } from 'react'
import { IconCheck, IconChevronDown, IconUserSearch } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/core/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/core/ui/popover'
import { cn } from '@/lib/utils'

import type { ClientRecord } from '@/app/actions/custom/clients'

interface ClientComboboxProps {
  clients: ClientRecord[]
  value: string // selected client id (stringified) or '' when none picked
  onValueChange: (id: string) => void
  disabled?: boolean
  id?: string
  placeholder?: string
}

/**
 * Client picker that lets the operator type to filter and click to select.
 * Selection is restricted to existing clients — typing a name that doesn't
 * match anything just narrows the list to "No se encontraron clientes" and
 * keeps the previous selection until they pick another one. New clients
 * still go through `/clients/new`.
 */
export function ClientCombobox({
  clients,
  value,
  onValueChange,
  disabled,
  id,
  placeholder = 'Elegí un cliente',
}: ClientComboboxProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')

  const selected = useMemo(
    () => clients.find(c => c.id.toString() === value) ?? null,
    [clients, value]
  )

  // Light-touch search: name + company + email + cuit, case-insensitive.
  const matches = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return clients
    return clients.filter(c => {
      const haystack = [c.name, c.company ?? '', c.email, c.cuit ?? '']
        .join(' ')
        .toLowerCase()
      return haystack.includes(q)
    })
  }, [clients, query])

  const triggerLabel = selected ? formatClientLabel(selected) : placeholder

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          id={id}
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled || clients.length === 0}
          className={cn(
            'w-full justify-between font-normal',
            !selected && 'text-muted-foreground'
          )}
        >
          <span className="flex items-center gap-2 truncate">
            <IconUserSearch className="size-4 shrink-0 opacity-50" />
            <span className="truncate">{triggerLabel}</span>
          </span>
          <IconChevronDown className="ml-2 size-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Buscar por nombre, empresa, email o CUIT..."
            value={query}
            onValueChange={setQuery}
          />
          <CommandList>
            <CommandEmpty>No se encontraron clientes.</CommandEmpty>
            <CommandGroup>
              {matches.map(client => {
                const isSelected = selected?.id === client.id
                return (
                  <CommandItem
                    key={client.id}
                    value={client.id.toString()}
                    onSelect={() => {
                      onValueChange(client.id.toString())
                      setOpen(false)
                      setQuery('')
                    }}
                  >
                    <IconCheck
                      className={cn(
                        'size-4',
                        isSelected ? 'opacity-100' : 'opacity-0'
                      )}
                    />
                    <div className="flex flex-col">
                      <span className="text-sm">{formatClientLabel(client)}</span>
                      {client.email && (
                        <span className="text-xs text-muted-foreground">{client.email}</span>
                      )}
                    </div>
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

function formatClientLabel(client: ClientRecord): string {
  return client.company ? `${client.name} — ${client.company}` : client.name
}
