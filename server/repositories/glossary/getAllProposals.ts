import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import type { IProposal } from '#shared/types/IProposal'

// Every full proposal (37 MB): only the free-text proposal filter needs their wording.
export const getAllProposals = cachedAsset(async () => {
    const entryIds = [...new Set((await getProposalIndex()).map(row => row.entryId))]
    return (await Promise.all(entryIds.map(id => readGlossaryAsset<IProposal[]>(`proposals/${id}.json`))))
        .flatMap(items => items || [])
})
