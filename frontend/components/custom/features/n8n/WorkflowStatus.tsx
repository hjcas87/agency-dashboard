'use client'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import type { TaskStatusResponse } from '@/lib/custom/features/n8n/types'
import { getTaskStateLabel, getTaskStateColor } from '@/lib/custom/utils/taskStateUtils'

interface WorkflowStatusProps {
  status: TaskStatusResponse
}

export function WorkflowStatus({ status }: WorkflowStatusProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Estado de la tarea</CardTitle>
          <span className={`font-bold ${getTaskStateColor(status.state)}`}>
            {getTaskStateLabel(status.state)}
          </span>
        </div>
        {status.status && <CardDescription>{status.status}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-4">
        {status.state === 'SUCCESS' && status.result && (
          <div className="p-3 bg-green-50 rounded border border-green-200">
            <p className="text-sm font-medium text-green-800 mb-2">Resultado:</p>
            <pre className="text-xs overflow-auto text-green-700">
              {JSON.stringify(status.result, null, 2)}
            </pre>
          </div>
        )}

        {status.state === 'FAILURE' && status.error && (
          <div className="p-3 bg-red-50 rounded border border-red-200">
            <p className="text-sm font-medium text-red-800 mb-2">Error:</p>
            <p className="text-xs text-red-700">{status.error}</p>
          </div>
        )}

        <details className="cursor-pointer">
          <summary className="text-xs text-muted-foreground hover:text-foreground">
            Ver detalles completos
          </summary>
          <pre className="text-xs overflow-auto mt-2 p-2 bg-muted rounded">
            {JSON.stringify(status, null, 2)}
          </pre>
        </details>
      </CardContent>
    </Card>
  )
}
