import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

export interface IProposalReviewEvent extends Omit<IProposalReview, 'verdict'> {
    verdict: TReviewVerdict | null
    previousReviewId: string | null
    undoneReviewId: string | null
}
