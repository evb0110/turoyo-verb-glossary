import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

export interface IProposalReview {
    id: string
    proposalId: string
    entryId: string
    userId: string
    userName: string
    verdict: TReviewVerdict
    comment: string | null
    createdAt: string
}
