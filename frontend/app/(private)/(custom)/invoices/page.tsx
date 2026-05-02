import { IconPlus } from '@tabler/icons-react'

import { Button } from '@/components/core/ui/button'
import { Card, CardContent } from '@/components/core/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/core/ui/tabs'

import { getBillableProposals, getInvoices } from '@/app/actions/custom/invoices'
import { BillableProposalsTable } from '@/components/custom/features/invoices/billable-proposals-table'
import { InvoicesTable } from '@/components/custom/features/invoices/invoices-table'

export default async function InvoicesPage() {
  const [invoices, billable] = await Promise.all([getInvoices(), getBillableProposals()])

  return (
    <div className="flex w-full flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Facturación</h1>
          <p className="text-sm text-muted-foreground">
            Emití Facturas C contra AFIP desde un presupuesto aprobado o manualmente.
          </p>
        </div>
        <Button asChild>
          <a href="/invoices/new">
            <IconPlus data-icon="inline-start" />
            Nueva factura manual
          </a>
        </Button>
      </div>

      <Tabs defaultValue="emitted">
        <TabsList>
          <TabsTrigger value="emitted">Emitidas ({invoices.length})</TabsTrigger>
          <TabsTrigger value="billable">Presupuestos facturables ({billable.length})</TabsTrigger>
        </TabsList>
        <TabsContent value="emitted">
          <Card>
            <CardContent>
              <InvoicesTable invoices={invoices} />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="billable">
          <Card>
            <CardContent>
              <BillableProposalsTable proposals={billable} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
