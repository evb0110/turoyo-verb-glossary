import type { IBox } from '#shared/types/IBox'
import type { IExample } from '#shared/types/IExample'
import type { IProposal } from '#shared/types/IProposal'
import type { IStem } from '#shared/types/IStem'
import { glossarySenses } from '#shared/utils/glossarySenses'

function changesMeaning(item: IProposal) {
    return ['new-sense', 'gloss-change'].includes(item.kind) || ['gloss', 'senses', 'sensesRaw'].includes(item.target.field || '')
}

function senseKey(box: IBox, example: IExample) {
    return example.sense ? `${box.detransitive ? 'D' : ''}${example.sense}` : '?'
}

// Places each suggestion beside the material it changes: an example, a form within a
// meaning, a meaning, or otherwise the stem as a whole.
export function stemLayout(stem: IStem, proposals: IProposal[]) {
    const exampleIds = new Set(stem.boxes.flatMap(box => box.examples.map(example => example.id)))
    const boxIds = new Set(stem.boxes.map(box => box.id))
    const byExample = new Map<string, IProposal[]>()
    const bySense = new Map<string, IProposal[]>()
    const byBox = new Map<string, IProposal[]>()
    const remaining: IProposal[] = []
    function push(map: Map<string, IProposal[]>, key: string, item: IProposal) {
        map.set(key, [...(map.get(key) || []), item])
    }
    for (const item of proposals) {
        const {
            exampleId,
            boxId,
            sense,
        } = item.target
        if (exampleId && exampleIds.has(exampleId)) push(byExample, exampleId, item)
        else if (sense && !boxId) push(bySense, sense, item)
        else if (boxId && boxIds.has(boxId)) push(byBox, `${boxId}|${sense || '?'}`, item)
        else remaining.push(item)
    }
    const rows = glossarySenses(stem).map(sense => ({
        ...sense,
        proposed: false,
    }))
    const keys = [...bySense.keys(), ...[...byBox.keys()].map(key => key.split('|').at(-1)!)]
    for (const key of keys) {
        if (rows.some(row => row.key === key)) continue
        // A suggested meaning such as "1b" goes after the last meaning that sorts before it.
        const after = rows.findLastIndex(row => row.key.localeCompare(key, 'en', { numeric: true }) < 0)
        rows.splice(after + 1, 0, {
            n: key,
            key,
            gloss: '',
            proposed: true,
        })
    }
    const senses = rows.map((sense) => {
        const groups = stem.boxes.map(box => ({
            box,
            id: `${stem.id}-cell-${sense.key}-${box.id}`,
            examples: box.examples
                .filter(example => senseKey(box, example) === sense.key)
                .map(example => ({
                    example,
                    proposals: byExample.get(example.id) || [],
                })),
            proposals: byBox.get(`${box.id}|${sense.key}`) || [],
        })).filter(group => group.examples.length || group.proposals.length)
        const own = bySense.get(sense.key) || []
        return {
            ...sense,
            id: `${stem.id}-sense-${sense.key}`,
            // Changes to the meaning itself sit under its heading; notes, questions and new
            // forms follow its examples.
            lead: own.filter(changesMeaning),
            trail: own.filter(item => !changesMeaning(item)),
            groups,
            all: [
                ...(bySense.get(sense.key) || []),
                ...groups.flatMap(group => [
                    ...group.examples.flatMap(item => item.proposals),
                    ...group.proposals,
                ]),
            ],
        }
    })
    return {
        stem,
        senses,
        remaining,
    }
}
