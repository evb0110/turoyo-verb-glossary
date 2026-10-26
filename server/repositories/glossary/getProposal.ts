import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import type { IProposal } from '#shared/types/IProposal'

export async function getProposal(id: string): Promise<IProposal | null> {
    const row = (await getProposalIndex()).find(item => item.id === id)
    if (!row) return null
    return (await getEntryProposals(row.entryId)).find(item => item.id === id) || null
}
