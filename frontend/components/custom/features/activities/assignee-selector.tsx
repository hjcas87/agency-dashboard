'use client'

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/core/ui/select'
import type { UserOption } from '@/app/actions/custom/activities'

const UNASSIGNED_VALUE = '__unassigned__'

interface AssigneeSelectorProps {
  users: UserOption[]
  value: number | null | undefined
  onChange: (userId: number | null) => void
  disabled?: boolean
}

export function AssigneeSelector({ users, value, onChange, disabled }: AssigneeSelectorProps) {
  const selectValue = value != null ? String(value) : UNASSIGNED_VALUE

  function handleChange(val: string) {
    onChange(val === UNASSIGNED_VALUE ? null : Number(val))
  }

  return (
    <Select value={selectValue} onValueChange={handleChange} disabled={disabled}>
      <SelectTrigger>
        <SelectValue placeholder="Sin asignar" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={UNASSIGNED_VALUE}>Sin asignar</SelectItem>
        {users.map(user => (
          <SelectItem key={user.id} value={String(user.id)}>
            {user.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
