export interface TaskStatusResponse {
  task_id: string
  state: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" | "RETRY" | "REVOKED"
  result?: Record<string, unknown>
  error?: string
  status?: string
}

export interface N8NTriggerRequest {
  webhook_path: string
  payload?: Record<string, unknown>
}

export interface N8NTriggerResponse {
  task_id: string
  status: string
  message?: string
}
