import { notFound } from 'next/navigation'
import { getClient } from '@/app/actions/custom/clients'
import { ClientEditForm } from '@/components/custom/features/clients/client-edit-form'

export default async function EditClientPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const clientId = parseInt(id, 10)

  if (isNaN(clientId)) {
    notFound()
  }

  let client
  try {
    client = await getClient(clientId)
  } catch {
    notFound()
  }

  return <ClientEditForm client={client} />
}
