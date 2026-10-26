import type { IProposal } from '#shared/types/IProposal'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { IProposalSummary } from '#shared/types/IProposalSummary'
import type { TProposalGroup } from '#shared/types/TProposalGroup'

export function summarizeProposals(
    proposals: IProposal[],
    matching: IProposal[],
    reviews: IProposalReview[],
    userId: string,
    resumeId: string,
    resumeGroup: string
): IProposalSummary {
    // The review queue uses the latest team decision; the home count is personal.
    // Sets also exclude superseded decisions and reviews of removed proposals.
    const ids = new Set(proposals.map(item => item.id))
    const decided = new Set(reviews.filter(item => ids.has(item.proposalId)).map(item => item.proposalId))
    const ownDecided = new Set(reviews.filter(item => item.userId === userId && ids.has(item.proposalId))
        .map(item => item.proposalId))
    const groups = new Map<TProposalGroup, { total: number
        undecided: number }>()
    for (const proposal of matching) {
        const kinds: TProposalGroup[] = proposal.priority === 1 ? [proposal.kind, 'important'] : [proposal.kind]
        for (const kind of kinds) {
            const count = groups.get(kind) || {
                total: 0,
                undecided: 0,
            }
            count.total++
            if (!decided.has(proposal.id)) count.undecided++
            groups.set(kind, count)
        }
    }
    const remembered = proposals.find(item => item.id === resumeId
        && (resumeGroup === 'important' ? item.priority === 1 : item.kind === resumeGroup))
    return {
        total: proposals.length,
        decided: decided.size,
        ownDecided: ownDecided.size,
        groups: [...groups].map(([kind, counts]) => ({
            kind,
            ...counts,
        })),
        resume: remembered
            ? {
                    group: resumeGroup,
                    id: remembered.id,
                }
            : null,
    }
}
