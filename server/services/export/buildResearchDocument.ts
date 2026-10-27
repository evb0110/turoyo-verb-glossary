import { exportFront } from '~~/server/services/export/exportFront'
import type { collectResearchNotes } from '~~/server/services/glossary/collectResearchNotes'
import { researchQuestion } from '~~/server/services/glossary/researchQuestion'
import type { IExportContext } from '~~/server/types/export/IExportContext'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'
import { rootLetter } from '#shared/utils/rootLetter'

interface IResearchDocumentInput {
    notes: ReturnType<typeof collectResearchNotes> // already filtered, in corpus order
    question: string
    root: string
    order: string[] // entry ids in glossary order
    context: IExportContext
}

// The readers' observations for a research question and/or root filter, letter > root, each note with its verse.
export function buildResearchDocument(input: IResearchDocumentInput): IExportDocument {
    const position = new Map(input.order.map((id, n) => [id, n]))
    const roots = new Map<string, typeof input.notes>()
    for (const note of input.notes)
        roots.set(note.occurrence.root, [...(roots.get(note.occurrence.root) || []), note])
    const sorted = [...roots].toSorted(([a, left], [b, right]) =>
        (position.get(left[0]!.occurrence.entryId || '') ?? Infinity)
        - (position.get(right[0]!.occurrence.entryId || '') ?? Infinity) || a.localeCompare(b))
    const letters = new Map<string, typeof sorted>()
    for (const item of sorted) letters.set(rootLetter(item[0]), [...(letters.get(rootLetter(item[0])) || []), item])
    const blocks: TDocBlock[] = []
    for (const [letter, group] of letters) {
        blocks.push({
            type: 'heading',
            level: 1,
            id: `letter:${letter}`,
            runs: [{ text: letter }],
        })
        for (const [root, notes] of group) {
            blocks.push({
                type: 'heading',
                level: 2,
                id: `root:${root}`,
                runs: [{ text: `${root} (${notes.length})` }],
            })
            for (const note of notes) {
                const item = note.occurrence
                const questions = [...new Set(item.rq.map(researchQuestion))]
                blocks.push({
                    type: 'paragraph',
                    style: 'body',
                    runs: [
                        {
                            text: item.form,
                            italic: true,
                        },
                        { text: ` · ${item.observations || item.meaning}` },
                    ],
                })
                blocks.push({
                    type: 'paragraph',
                    style: 'exampleNote',
                    runs: [{
                        text: [
                            `${note.cite} ${note.title}`,
                            `Stem ${item.stem}${item.detransitive ? ', detransitive' : ''}`,
                            item.box,
                            `meaning ${item.sense}`,
                            item.observations ? item.meaning : '',
                            item.arguments,
                            questions.length > 1 || !input.question ? `questions: ${questions.join(', ')}` : '',
                        ].filter(Boolean).join(' · '),
                    }],
                })
            }
        }
    }
    const scope = [
        input.question ? `Question: ${input.question}` : 'All questions',
        input.root ? `roots beginning with ${input.root}` : '',
    ].filter(Boolean).join(', ')
    const name = [input.question || 'all', input.root ? `root-${input.root}` : ''].filter(Boolean).join('-')
    return {
        fileName: `turoyo-research-${name}`,
        title: 'Turoyo Verb Glossary: research notes',
        subject: `Research notes. ${scope}`,
        keywords: ['Turoyo', 'research notes', input.question].filter(Boolean),
        front: exportFront('Research notes', scope, [
            `${input.notes.length.toLocaleString('en')} observations by the corpus readers (a machine reading of the `
            + 'texts), grouped by root. Each gives the form, the observation, and the verse with its analysis.',
        ], input.context),
        contentsDepth: 2,
        headerLevel: 2,
        blocks,
    }
}
