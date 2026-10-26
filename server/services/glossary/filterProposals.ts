import type { IEntryIndex } from '#shared/types/IEntryIndex'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalFilters } from '#shared/types/IProposalFilters'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

export function filterProposals(proposals: IProposal[], index: IEntryIndex[], filters: IProposalFilters): IProposal[] {
    const root = normalizeTuroyo(filters.root)
    const text = filters.text.trim().toLowerCase()
    if (!root && !text) return proposals
    const roots = new Map(index.map(item => [item.id, item.root]))
    return proposals.filter(item =>
        normalizeTuroyo(roots.get(item.entryId) || item.entryId).includes(root)
        && (!text
            || item.evidence.some(ref => `${ref.textId} ${ref.cite}`.toLowerCase().includes(text))
            || `${item.before || ''} ${item.after || ''} ${item.summary} ${item.rationale}`.toLowerCase().includes(text))
    )
}
