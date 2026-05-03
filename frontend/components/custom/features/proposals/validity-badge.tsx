import { Badge } from "@/components/core/ui/badge"
import { PROPOSAL_MESSAGES } from "@/lib/messages"

interface ValidityBadgeProps {
  daysUntilExpiry: number | null | undefined
}

export function ValidityBadge({ daysUntilExpiry }: ValidityBadgeProps) {
  if (daysUntilExpiry === null || daysUntilExpiry === undefined) return null

  if (daysUntilExpiry > 5) {
    return (
      <Badge variant="secondary" className="bg-blue-100 text-blue-700 border-blue-200">
        {PROPOSAL_MESSAGES.validity.vigente}
      </Badge>
    )
  }

  if (daysUntilExpiry >= 1) {
    return (
      <Badge
        variant="outline"
        className="bg-amber-50 text-amber-700 border-amber-300"
      >
        {PROPOSAL_MESSAGES.validity.expiresSoon(daysUntilExpiry)}
      </Badge>
    )
  }

  return (
    <Badge variant="destructive">
      {PROPOSAL_MESSAGES.validity.expired(daysUntilExpiry)}
    </Badge>
  )
}
