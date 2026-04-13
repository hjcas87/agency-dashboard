import { getProposals } from '@/app/actions/custom/proposals'
import { ProposalsTable, type Proposal } from '@/components/custom/features/proposals/proposals-table'

export default async function ProposalsPage() {
  const proposals = await getProposals()

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold">Presupuestos</h1>
        <p className="text-muted-foreground">
          Gestioná tus presupuestos y cotizaciones.
        </p>
      </div>
      <ProposalsTable data={proposals as Proposal[]} />
    </div>
  )
}
