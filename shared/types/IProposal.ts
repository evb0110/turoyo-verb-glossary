import type { TProposalKind } from '#shared/types/TProposalKind'

export interface IProposal {
    id: string
    entryId: string
    kind: TProposalKind
    stage: 'synthesis' | 'citation-check' | 'proofreading'
    target: { stemId?: string
        boxId?: string
        exampleId?: string
        sense?: string
        field?: string }
    summary: string
    before: string | null
    after: string | null
    data: Record<string, unknown>
    rationale: string
    evidence: Array<{ textId: string
        v: number
        cite: string }>
    priority: 1 | 2 | 3
    provenance: { model: string
        effort: string
        protocol: string
        run: string
        date: string }
}
