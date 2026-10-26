import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'

export interface IProposalDetail {
    proposal: IProposal
    entry: IEntry | null
}
