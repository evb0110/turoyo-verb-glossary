import { entryBlocks } from '~~/server/services/export/entryBlocks'
import { exportFront } from '~~/server/services/export/exportFront'
import type { IExportContext } from '~~/server/types/export/IExportContext'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'
import type { IEntry } from '#shared/types/IEntry'
import { rootLetter } from '#shared/utils/rootLetter'

interface IGlossaryDocumentInput {
    entries: IEntry[] // in glossary order
    scope: string // "The whole glossary", "Letter ʔ", "Volume 1 (ʔ, ʕ, b, č)"
    fileName: string
    totalRoots: number
    context: IExportContext
}

// The glossary or a part of it: letter > root > stem > meaning, with form labels in the text.
export function buildGlossaryDocument(input: IGlossaryDocumentInput): IExportDocument {
    const letters = new Map<string, IEntry[]>()
    for (const entry of input.entries) {
        const letter = rootLetter(entry.root)
        letters.set(letter, [...(letters.get(letter) || []), entry])
    }
    const blocks: TDocBlock[] = []
    for (const [letter, entries] of letters) {
        blocks.push({
            type: 'heading',
            level: 1,
            id: `letter:${letter}`,
            runs: [{ text: letter }],
        })
        for (const entry of entries) blocks.push(...entryBlocks({
            id: entry.id,
            root: entry.root,
            entry,
            proposals: null,
            reviews: new Map(),
            level: 2,
        }))
    }
    const count = input.entries.length.toLocaleString('en')
    return {
        fileName: input.fileName,
        title: 'Turoyo Verb Glossary',
        subject: `${input.scope}: ${count} roots`,
        keywords: ['Turoyo', 'verb', 'glossary'],
        front: exportFront('Turoyo Verb Glossary', input.scope, [
            `${count} of ${input.totalRoots.toLocaleString('en')} roots, as the team wrote them, without machine `
            + 'suggestions. “See also” references link to their root when it is in this document.',
        ], input.context),
        contentsDepth: 2,
        headerLevel: 2,
        blocks,
    }
}
