import { TASK_STATE } from "@/lib/messages"

export function getTaskStateLabel(state: string): string {
  return TASK_STATE[state as keyof typeof TASK_STATE]?.label ?? state
}

export function getTaskStateColor(state: string): string {
  return TASK_STATE[state as keyof typeof TASK_STATE]?.color ?? "text-gray-600"
}
