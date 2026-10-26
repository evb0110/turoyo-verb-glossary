import type { TProposalGroup } from '#shared/types/TProposalGroup'

export interface IProposalGroup {
    kind: TProposalGroup
    total: number
    undecided: number
}
