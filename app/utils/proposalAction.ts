import type { IProposal } from '#shared/types/IProposal'

const fieldNames: Record<string, string> = {
    turoyo: 'the Turoyo',
    translation: 'the translation',
    refs: 'the reference',
    forms: 'the forms',
    head: 'the heading',
    gloss: 'the meaning',
    senses: 'the meanings',
    sensesRaw: 'the meanings',
    note: 'the note',
    idiom: 'the idiom',
}

// What accepting a suggestion does, in a few words: "Add this example", "Correct the translation".
// Notes and questions change nothing, so they say whom they are for.
export function proposalAction(proposal: IProposal) {
    const {
        kind,
        target,
        data,
    } = proposal
    const sense = target.sense || (typeof data.label === 'string' ? data.label : '')
    const form = typeof data.box === 'string' ? `${data.detransitive ? 'Detransitive ' : ''}${data.box}` : ''
    const stem = typeof data.stem === 'string' ? data.stem : target.stemId?.split('.').at(-1)?.replace(/~\d+$/u, '') || ''
    const actions: Record<IProposal['kind'], string> = {
        'add-example': 'Add this example',
        'new-form': form ? `Add the form ${form} with this example` : 'Add a new form with this example',
        'new-sense': sense ? `Add meaning ${sense}` : 'Add this meaning',
        'gloss-change': sense ? `Change the wording of meaning ${sense}` : 'Change the wording of this meaning',
        'new-idiom': 'Add this idiom',
        'new-stem': stem ? `Add Stem ${stem}` : 'Add this stem',
        'new-root': 'Add this verb',
        'fix-text': `Correct ${(target.field && fieldNames[target.field]) || 'the wording'}`,
        'fix-citation': 'Correct the reference',
        'fix-structure': 'Change the layout',
        'move-example': 'Move this example',
        'duplicate-entry': 'Possible duplicate',
        'question': 'Question for the editors',
        'note': 'Note for the editors',
    }
    return actions[kind]
}
