import type { IProposalGroup } from '#shared/types/IProposalGroup'

export interface IProposalSummary {
    total: number
    decided: number
    ownDecided: number
    groups: IProposalGroup[]
    resume: { group: string
        id: string } | null
}
