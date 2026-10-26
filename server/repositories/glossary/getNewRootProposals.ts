import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import type { IProposal } from '#shared/types/IProposal'

// The "new-root" proposal of every verb that is not in the glossary yet, one per verb.
export const getNewRootProposals = cachedAsset(async () => {
    const known = new Set((await getEntryIndex()).map(entry => entry.id))
    const ids = new Set((await getProposalIndex())
        .filter(row => row.kind === 'new-root' && !known.has(row.entryId))
        .map(row => row.entryId))
    const proposals: IProposal[] = []
    for (const id of ids) {
        const proposal = (await getEntryProposals(id)).find(item => item.kind === 'new-root')
        if (proposal) proposals.push(proposal)
    }
    return proposals
})
