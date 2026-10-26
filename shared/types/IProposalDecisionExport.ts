import type { IProposal } from '#shared/types/IProposal'
import type { IProposalEdit } from '#shared/types/IProposalEdit'
import type { IProposalReview } from '#shared/types/IProposalReview'

export interface IProposalDecisionExport {
    proposalId: string
    verb: string
    kind: string
    citationTarget: { target: IProposal['target']
        citations: IProposal['evidence'] }
    machineText: IProposalEdit | null
    editedText: IProposalEdit | null
    verdict: IProposalReview['verdict']
    comment: string | null
    reviewer: string
    reviewerId: string | null
    date: string
}
