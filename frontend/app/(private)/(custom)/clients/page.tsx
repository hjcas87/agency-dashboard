import { getClients } from '@/app/actions/custom/clients'
import { ClientsTable, type Client } from '@/components/custom/features/clients/clients-table'

export default async function ClientsPage() {
  const clients = await getClients()

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold">Clientes</h1>
        <p className="text-muted-foreground">
          Gestioná tus clientes y su información de contacto.
        </p>
      </div>
      <ClientsTable data={clients as Client[]} />
    </div>
  )
}
