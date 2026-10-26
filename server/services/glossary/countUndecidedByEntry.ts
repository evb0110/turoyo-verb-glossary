import type { IProposalIndex } from '#shared/types/IProposalIndex'
import type { IProposalReview } from '#shared/types/IProposalReview'

// Undecided suggestions per entry. Decisions on proposals no longer in the static index are ignored.
export function countUndecidedByEntry(proposals: IProposalIndex[], reviews: IProposalReview[]): Record<string, number> {
    const decided = new Set(reviews.map(review => review.proposalId))
    const counts: Record<string, number> = {}
    for (const proposal of proposals)
        if (!decided.has(proposal.id)) counts[proposal.entryId] = (counts[proposal.entryId] || 0) + 1
    return counts
}
