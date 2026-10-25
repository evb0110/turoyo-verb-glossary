import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import { glossarySenses } from '#shared/utils/glossarySenses'

export function proposalContext(entry: IEntry | null, proposal: IProposal) {
    const stem
        = entry?.stems.find(
            item =>
                item.id === proposal.target.stemId
                || proposal.target.boxId?.startsWith(`${item.id}.`)
                || proposal.target.exampleId?.startsWith(`${item.id}.`)
        ) || null
    const box
        = stem?.boxes.find(
            item =>
                item.id === proposal.target.boxId
                || proposal.target.exampleId?.startsWith(`${item.id}.`)
        ) || null
    const example
        = box?.examples.find(item => item.id === proposal.target.exampleId) || null
    const idiom
        = entry?.idioms.find(item => item.id === proposal.target.exampleId) || null
    const senseKey
        = proposal.target.sense
            || (example?.sense ? `${box?.detransitive ? 'D' : ''}${example.sense}` : '')
    const sense = stem
        ? glossarySenses(stem).find(item => item.key === senseKey) || null
        : null
    const location = [
        stem && `Stem ${stem.stem}`,
        box && `${box.detransitive ? 'Detransitive · ' : ''}${box.label}`,
        sense && `meaning ${sense.key}: ${sense.gloss}`,
        idiom && 'Idiomatic phrase',
    ]
        .filter(Boolean)
        .join(' · ')
    const field = proposal.target.field
    const current
        = field === 'translation'
            ? example?.translation
            : field === 'refs'
                ? example?.refs.map(ref => ref.raw).join('; ')
                : field === 'forms'
                    ? stem?.forms
                    : field === 'head'
                        ? entry?.head
                        : ['gloss', 'senses', 'sensesRaw'].includes(field || '')
                                ? sense?.gloss || stem?.sensesRaw
                                : field === 'note'
                                    ? example?.note
                                    : example?.turoyo || idiom?.raw
    return {
        stem,
        box,
        example,
        idiom,
        sense,
        location,
        current: current || proposal.before || '',
    }
}
