import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import type { IStem } from '#shared/types/IStem'
import { stemLayout } from '#shared/utils/stemLayout'

// Where each suggestion of an entry goes: under its stem (by meaning, form and example), with the idioms,
// or with the notes and questions about the entry as a whole. A suggested new stem appears as an empty stem.
export function entryLayout(entry: IEntry | null, proposals: IProposal[]) {
    const stems: IStem[] = [...(entry?.stems || [])]
    for (const proposal of proposals)
        if (proposal.kind === 'new-stem' && proposal.target.stemId
            && !stems.some(stem => stem.id === proposal.target.stemId))
            stems.push({
                id: proposal.target.stemId,
                stem: String(proposal.data.stem || proposal.target.stemId.split('.').at(-1)),
                forms: '',
                senses: [],
                sensesRaw: '',
                detransitiveSenses: [],
                detransitiveSensesRaw: null,
                boxes: [],
                notes: [],
            })
    function proposalStem(proposal: IProposal) {
        return stems.find(stem =>
            proposal.target.stemId === stem.id
            || proposal.target.boxId?.startsWith(`${stem.id}.`)
            || proposal.target.exampleId?.startsWith(`${stem.id}.`)
        )?.id
    }
    function isIdiom(proposal: IProposal) {
        return proposal.kind === 'new-idiom'
            || !!entry?.idioms.some(item => item.id === proposal.target.exampleId)
            || !!proposal.target.exampleId?.includes('.idiom.')
    }
    const idiomProposals = proposals.filter(isIdiom)
    return {
        layouts: stems.map(stem => stemLayout(
            stem,
            proposals.filter(item => !isIdiom(item) && proposalStem(item) === stem.id)
        )),
        idiomProposals,
        unplacedIdiomProposals: idiomProposals
            .filter(item => !entry?.idioms.some(idiom => idiom.id === item.target.exampleId)),
        entryProposals: proposals.filter(item => !isIdiom(item) && !proposalStem(item)),
        notes: (entry?.notes || []).filter(note => !/^idiomatic phrases\s*[:.]?$/iu.test(note.trim())),
    }
}
