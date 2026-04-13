import { notFound } from 'next/navigation'
import { ProposalEditForm } from '@/components/custom/features/proposals/proposal-edit-form'
import { getProposal } from '@/app/actions/custom/proposals'

export default async function EditProposalPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const proposalId = parseInt(id, 10)

  if (isNaN(proposalId)) {
    notFound()
  }

  let proposal
  try {
    proposal = await getProposal(proposalId)
  } catch {
    notFound()
  }

  return <ProposalEditForm proposal={proposal} />
}
