import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import { normalizeProposal } from '~~/server/services/glossary/normalizeProposal'
import type { IProposal } from '#shared/types/IProposal'

export async function getEntryProposals(entryId: string): Promise<IProposal[]> {
    if (!(await getProposalIndex()).some(row => row.entryId === entryId)) return []
    return ((await readGlossaryAsset<IProposal[]>(`proposals/${entryId}.json`)) || []).map(normalizeProposal)
}
