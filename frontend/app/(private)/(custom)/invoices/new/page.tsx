import { getClients } from '@/app/actions/custom/clients'
import { ManualInvoiceForm } from '@/components/custom/features/invoices/manual-invoice-form'

export default async function NewInvoicePage() {
  const clients = await getClients()
  return <ManualInvoiceForm clients={clients} />
}
