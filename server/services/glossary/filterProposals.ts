import type { IEntryIndex } from '#shared/types/IEntryIndex'
import type { IProposalIndex } from '#shared/types/IProposalIndex'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

// textMatches: ids of the proposals matching the text filter, or null when there is none.
export function filterProposals(
    proposals: IProposalIndex[],
    index: IEntryIndex[],
    rootFilter: string,
    textMatches: ReadonlySet<string> | null
): IProposalIndex[] {
    const root = normalizeTuroyo(rootFilter)
    if (!root && !textMatches) return proposals
    const roots = new Map(index.map(item => [item.id, item.root]))
    return proposals.filter(item =>
        normalizeTuroyo(roots.get(item.entryId) || item.entryId).includes(root)
        && (!textMatches || textMatches.has(item.id))
    )
}
