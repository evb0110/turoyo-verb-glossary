import type { IProposalEdit } from '#shared/types/IProposalEdit'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

export interface IProposalReview {
    id: string
    proposalId: string
    entryId: string
    userId: string | null
    userName: string
    verdict: TReviewVerdict
    edited: IProposalEdit | null
    comment: string | null
    createdAt: string
}
