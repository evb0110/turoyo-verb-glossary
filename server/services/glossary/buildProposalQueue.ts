import type { IProposalIndex } from '#shared/types/IProposalIndex'
import type { IProposalQueue } from '#shared/types/IProposalQueue'

export function buildProposalQueue(proposals: IProposalIndex[], group: string, proposalId: string): IProposalQueue {
    const selected = group || proposals.find(item => item.id === proposalId)?.kind || ''
    return {
        group: selected,
        ids: proposals.filter(item => selected === 'important' ? item.priority === 1 : item.kind === selected)
            .toSorted((a, b) => a.priority - b.priority || a.id.localeCompare(b.id))
            .map(item => item.id),
    }
}
