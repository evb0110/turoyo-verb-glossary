import type { IProposalReview } from '#shared/types/IProposalReview'
import type { IProposalReviewEvent } from '#shared/types/IProposalReviewEvent'

// Only the explicitly enabled development auth bypass uses this process-local store.
export const devReviews = {
    current: new Map<string, IProposalReview>(),
    events: [] as IProposalReviewEvent[],
}
