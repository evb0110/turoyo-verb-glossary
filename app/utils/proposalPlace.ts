import type { TProposalPlacement } from '~/types/TProposalPlacement'
import type { IProposal } from '#shared/types/IProposal'
import type { proposalContext } from '#shared/utils/proposalContext'

// The levels a card has to name because its position on the page does not show them.
const unshown: Record<TProposalPlacement, Array<'stem' | 'meaning' | 'form'>> = {
    example: [],
    form: [],
    meaning: ['form'],
    stem: ['meaning', 'form'],
    entry: ['stem', 'meaning', 'form'],
    queue: [],
}

// The part of a suggestion's location that the card's place on the page leaves out, such as
// "meaning 2, Infectum" for a card listed with its stem as a whole. Empty when the place says it all.
export function proposalPlace(
    context: ReturnType<typeof proposalContext>,
    proposal: IProposal,
    placement: TProposalPlacement
) {
    const levels = unshown[placement]
    const {
        stem,
        box,
        example,
    } = context
    const {
        kind,
        target,
        data,
    } = proposal
    const stemLabel = stem?.stem || target.stemId?.split('.').at(-1)?.replace(/~\d+$/u, '')
    const form = box
        ? `${box.detransitive ? 'Detransitive ' : ''}${box.label}`
        : typeof data.box === 'string' ? `${data.detransitive ? 'Detransitive ' : ''}${data.box}` : ''
    const sense = target.sense || (example?.sense ? `${box?.detransitive ? 'D' : ''}${example.sense}` : '')
    // A new stem, meaning or form already names itself in the card's action.
    return [
        levels.includes('stem') && kind !== 'new-stem' && stemLabel && `Stem ${stemLabel}`,
        levels.includes('meaning') && !['new-sense', 'gloss-change'].includes(kind) && sense && `meaning ${sense}`,
        levels.includes('form') && kind !== 'new-form' && form,
    ].filter(Boolean).join(', ')
}
