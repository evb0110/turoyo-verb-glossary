import type { IProposal } from '#shared/types/IProposal'
import type { proposalContext } from '#shared/utils/proposalContext'

const fieldLabels: Record<string, string> = {
    turoyo: 'Turoyo',
    translation: 'translation',
    refs: 'reference',
    forms: 'forms',
    head: 'heading',
    gloss: 'meaning',
    senses: 'meanings',
    sensesRaw: 'meanings',
    note: 'note',
}

// A short location such as "Stem I · meaning 2 · Infectum · example 11 · translation".
export function proposalTarget(context: ReturnType<typeof proposalContext>, proposal: IProposal) {
    const {
        stem,
        box,
        example,
        idiom,
    } = context
    const {
        target,
        data,
    } = proposal
    const stemLabel = stem?.stem || target.stemId?.split('.').at(-1)?.replace(/~\d+$/u, '')
    const boxLabel = box
        ? `${box.detransitive ? 'Detransitive ' : ''}${box.label}`
        : typeof data.box === 'string' ? `${data.detransitive ? 'Detransitive ' : ''}${data.box}` : ''
    const sense = target.sense || (example?.sense ? `${box?.detransitive ? 'D' : ''}${example.sense}` : '')
    const field = target.field ? fieldLabels[target.field] || target.field : ''
    return [
        stemLabel && `Stem ${stemLabel}`,
        sense && `meaning ${sense}`,
        boxLabel,
        example && `example ${example.id.split('.').at(-1)}`,
        idiom && 'idiom',
        // "meaning 2 · meaning" says the same twice.
        !(sense && field === 'meaning') && field,
    ].filter(Boolean).join(' · ')
}
