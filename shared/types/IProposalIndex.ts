import type { IProposal } from '#shared/types/IProposal'

export interface IProposalIndex {
    id: string
    entryId: string
    kind: IProposal['kind']
    stage: IProposal['stage']
    priority: IProposal['priority']
    summary: string
    texts: string[]
}
