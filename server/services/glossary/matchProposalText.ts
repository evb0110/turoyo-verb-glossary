import type { IProposal } from '#shared/types/IProposal'

export function matchProposalText(proposals: IProposal[], filter: string): Set<string> {
    const text = filter.trim().toLowerCase()
    return new Set(proposals.filter(item =>
        item.evidence.some(ref => `${ref.textId} ${ref.cite}`.toLowerCase().includes(text))
        || `${item.before || ''} ${item.after || ''} ${item.summary} ${item.rationale}`.toLowerCase().includes(text))
        .map(item => item.id))
}
