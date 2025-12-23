'use client'

import { Button } from '@/components/core/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/core/ui/card'
import { useState } from 'react'
import { useN8NWorkflow } from '@/lib/custom/features/n8n/useN8NWorkflow'
import { WorkflowStatus } from '@/components/custom/features/n8n/WorkflowStatus'

export default function Home() {
  const [initialResponse, setInitialResponse] = useState<unknown>(null)
  const { triggerWorkflow, taskStatus, error, isLoading } = useN8NWorkflow()

  const handleTriggerWorkflow = async () => {
    try {
      setInitialResponse(null)
      const response = await triggerWorkflow({
        webhook_path: 'webhook/348b0e40-cbbc-4146-97ad-e21d7b145ea9',
        payload: {
          message: 'Hello from Frontend!',
          timestamp: new Date().toISOString(),
        },
      })
      setInitialResponse(response)
    } catch (err) {
      // Error is handled by the hook
      console.error('Failed to trigger workflow:', err)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">Core Platform</h1>

        <Card className="mb-4">
          <CardHeader>
            <CardTitle>Forward Deployed Engineer Platform</CardTitle>
            <CardDescription>
              Boilerplate modular y extensible para desarrollo rápido
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Arquitectura:</h3>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li>Frontend: Next.js 15.5.9 con React 19.2.3</li>
                  <li>Backend: FastAPI modular</li>
                  <li>Automation: N8N self-hosted</li>
                  <li>Message Broker: Kafka</li>
                  <li>API Client: openapi-fetch (type-safe)</li>
                </ul>
              </div>

              <div className="pt-4 border-t">
                <Button
                  onClick={handleTriggerWorkflow}
                  disabled={isLoading}
                  className="w-full"
                >
                  {isLoading ? 'Procesando...' : 'Probar N8N Workflow'}
                </Button>

                {error && (
                  <div className="mt-4 p-4 bg-red-50 rounded-md border border-red-200">
                    <p className="text-sm font-medium text-red-800">Error:</p>
                    <p className="text-xs text-red-700 mt-1">{error.message}</p>
                  </div>
                )}

                {initialResponse && (
                  <div className="mt-4 p-4 bg-muted rounded-md">
                    <h4 className="font-semibold mb-2">Respuesta inicial:</h4>
                    <pre className="text-xs overflow-auto">
                      {JSON.stringify(initialResponse, null, 2)}
                    </pre>
                  </div>
                )}

                {taskStatus && <WorkflowStatus status={taskStatus} />}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
