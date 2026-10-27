import type { IProposalReview } from '#shared/types/IProposalReview'

// The first words of the line that says who decided what: "Accepted", "Marked to decide later".
export function decisionWords(review: IProposalReview, question: boolean) {
    if (review.verdict === 'accept') return question ? 'Noted' : review.edited ? 'Accepted with changes' : 'Accepted'
    if (review.verdict === 'reject') return question ? 'Dismissed' : 'Rejected'
    return question ? 'Marked to discuss later' : 'Marked to decide later'
}
