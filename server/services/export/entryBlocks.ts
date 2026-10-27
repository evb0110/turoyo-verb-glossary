import { proposalBlocks } from '~~/server/services/export/proposalBlocks'
import type { IDocRun } from '~~/server/types/export/IDocRun'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'
import type { TDocParagraphStyle } from '~~/server/types/export/TDocParagraphStyle'
import type { IEntry } from '#shared/types/IEntry'
import type { IExample } from '#shared/types/IExample'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalReview } from '#shared/types/IProposalReview'
import { entryLayout } from '#shared/utils/entryLayout'
import { idiomTokens } from '#shared/utils/idiomTokens'

interface IEntryBlocksInput {
    id: string
    root: string
    entry: IEntry | null
    proposals: IProposal[] | null // null: the entry only, without suggestions
    reviews: ReadonlyMap<string, IProposalReview>
    level: 1 | 2 // the heading level of the root
}

function exampleRuns(example: IExample): IDocRun[] {
    return [
        {
            text: example.turoyo || example.raw,
            italic: !!example.turoyo,
        },
        ...(example.translation ? [{ text: ` ‘${example.translation}’` }] : []),
        ...(example.refs.length ? [{ text: `  ${example.refs.map(ref => ref.raw).join('; ')}` }] : []),
    ]
}

// One glossary entry, root > stem > meaning > form as on the entry page, optionally with its suggestions
// placed beside the material they change. Heading ids start with "entry:" so cross-references can link to them.
export function entryBlocks(input: IEntryBlocksInput): TDocBlock[] {
    const {
        id,
        entry,
        level,
    } = input
    const blocks: TDocBlock[] = []
    const layout = entryLayout(entry, input.proposals || [])
    function paragraph(style: TDocParagraphStyle, runs: IDocRun[]) {
        blocks.push({
            type: 'paragraph',
            style,
            runs,
        })
    }
    // Below Heading 4 a heading becomes a form label in the text. The source repeats some meaning numbers
    // within a stem (e.g. dry, Stem I, "1." six times); a repeated id gets the occurrence number, "~2", "~3".
    const used = new Map<string, number>()
    function heading(depth: number, anchor: string, runs: IDocRun[]) {
        const headingLevel = level + depth
        const occurrence = (used.get(anchor) || 0) + 1
        used.set(anchor, occurrence)
        if (headingLevel > 4) paragraph('label', runs)
        else blocks.push({
            type: 'heading',
            level: headingLevel as 1 | 2 | 3 | 4,
            id: occurrence > 1 ? `${anchor}~${occurrence}` : anchor,
            runs,
        })
    }
    function suggestions(items: IProposal[]) {
        for (const item of items) blocks.push(...proposalBlocks(item, entry, input.reviews.get(item.id) || null))
    }

    heading(0, `entry:${id}`, [{ text: input.root }])
    if (entry?.head) paragraph('body', [{ text: entry.head }])
    if (!entry) paragraph('note', [{ text: 'Suggested new verb. This entry is not in the glossary yet.' }])
    if (entry?.crossRefs.length)
        paragraph('body', [
            { text: 'See also ' },
            ...entry.crossRefs.flatMap((ref, n) => [
                ...(n ? [{ text: ', ' }] : []),
                {
                    text: ref.replaceAll('-', ' '),
                    link: `entry:${ref}`,
                },
            ]),
        ])
    for (const stemLayout of layout.layouts) {
        const stem = stemLayout.stem
        heading(1, `stem:${stem.id}`, [
            { text: `Stem ${stem.stem}` },
            ...(stem.forms
                ? [{
                        text: `  ${stem.forms}`,
                        italic: true,
                    }]
                : []),
        ])
        for (const sense of stemLayout.senses) {
            heading(2, `sense:${stem.id}:${sense.key}`, [
                { text: sense.key === '?' ? '' : `${sense.key}. ` },
                { text: sense.proposed ? 'Suggested meaning, not in the glossary yet' : sense.gloss },
            ])
            suggestions(sense.lead)
            for (const group of sense.groups) {
                heading(3, `form:${group.id}`, [{ text: `${group.box.detransitive ? 'Detransitive · ' : ''}${group.box.label}` }])
                for (const item of group.examples) {
                    paragraph('example', exampleRuns(item.example))
                    if (item.example.note) paragraph('exampleNote', [{ text: item.example.note }])
                    suggestions(item.proposals)
                }
                suggestions(group.proposals)
            }
            suggestions(sense.trail)
        }
        if (stemLayout.remaining.length) {
            paragraph('label', [{ text: `Other suggestions for Stem ${stem.stem}` }])
            suggestions(stemLayout.remaining)
        }
        if (stem.notes.length) {
            paragraph('label', [{ text: 'Notes' }])
            for (const note of stem.notes) paragraph('body', [{ text: note }])
        }
    }
    if (entry?.idioms.length || layout.idiomProposals.length) {
        heading(1, `idioms:${id}`, [{ text: 'Idiomatic phrases' }])
        for (const idiom of entry?.idioms || []) {
            paragraph('example', idiomTokens(idiom.raw, new Set()).map(token => ({
                text: token.text,
                italic: token.kind === 'headword' || token.kind === 'turoyo',
                bold: token.kind === 'headword',
            })))
            suggestions(layout.idiomProposals.filter(item => item.target.exampleId === idiom.id))
        }
        suggestions(layout.unplacedIdiomProposals)
    }
    if (layout.notes.length || layout.entryProposals.length) {
        heading(1, `notes:${id}`, [{ text: layout.entryProposals.length ? 'Notes and questions for the editors' : 'Notes' }])
        for (const note of layout.notes) paragraph('body', [{ text: note }])
        suggestions(layout.entryProposals)
    }
    return blocks
}
