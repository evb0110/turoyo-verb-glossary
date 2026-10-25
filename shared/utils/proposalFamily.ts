import type { TProposalKind } from '#shared/types/TProposalKind'

export function proposalFamily(kind: TProposalKind): 'addition' | 'correction' | 'note' {
    if (kind === 'note' || kind === 'question') return 'note'
    return ['new-sense', 'add-example', 'new-idiom', 'new-stem', 'new-form', 'new-root'].includes(kind)
        ? 'addition'
        : 'correction'
}
