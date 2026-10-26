import type { IEntryIndex } from '#shared/types/IEntryIndex'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalIndex } from '#shared/types/IProposalIndex'
import type { IRootIndexRow } from '#shared/types/IRootIndexRow'

// The glossary roots, then the verbs only proposed so far, each with its number of suggestions.
export function buildRootIndex(
    entries: IEntryIndex[],
    proposals: IProposalIndex[],
    newRoots: IProposal[]
): IRootIndexRow[] {
    const counts = new Map<string, number>()
    for (const proposal of proposals) counts.set(proposal.entryId, (counts.get(proposal.entryId) || 0) + 1)
    return [
        ...entries.map(entry => ({
            ...entry,
            proposalCount: counts.get(entry.id) || 0,
        })),
        ...newRoots.map(proposal => ({
            id: proposal.entryId,
            root: String(proposal.data.root || proposal.entryId.replaceAll('-', ' ')),
            homonym: null,
            stems: [],
            glossPreview: proposal.summary,
            exampleCount: 0,
            volume: '',
            proposed: true,
            proposalCount: counts.get(proposal.entryId) || 0,
        })),
    ]
}
