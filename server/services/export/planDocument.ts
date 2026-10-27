import { assemblePart } from '~~/server/services/export/assemblePart'
import { estimateSize } from '~~/server/services/export/estimateSize'
import { headingChain } from '~~/server/services/export/headingChain'
import { packPieces } from '~~/server/services/export/packPieces'
import type { IDocHeading } from '~~/server/types/export/IDocHeading'
import type { IDocPiece } from '~~/server/types/export/IDocPiece'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { IPlannedPart } from '~~/server/types/export/IPlannedPart'
import type { TExportFormat } from '~~/server/types/export/TExportFormat'

// A Vercel function response may not exceed 4.5 MB; every file served stays under 4,000,000 bytes.
const LIMIT = 4_000_000
// The estimate aims a little lower, so that a part rarely has to be divided again once written.
const TARGET = 3_500_000

function variable(blocks: IExportDocument['blocks'], format: TExportFormat) {
    return estimateSize(blocks, format) - estimateSize([], format)
}

// The headings in force where a piece's content starts: its context and the headings it opens with.
function opening(piece: IDocPiece) {
    const lead = piece.blocks.findIndex(block => block.type !== 'heading')
    return headingChain(piece.context, piece.blocks.slice(0, lead < 0 ? piece.blocks.length : lead))
}

// "ʔ – h", "Jan 1.1 – Jan 2.3", or within one root "sym: Stem I – Stem III": the first and last section at the
// outermost level (letter, root or text, stem, meaning) where the part's first and last content differ.
function label(pieces: IDocPiece[]) {
    const name = (heading: IDocHeading | undefined) => {
        const text = (heading?.runs.map(run => run.text).join('') || '').split(' · ')[0]!
            .replace(/\s*\(\d+\)$/u, '').replace(/\s+/gu, ' ').trim()
        return text.length > 40 ? `${text.slice(0, 39).trim()}…` : text
    }
    const at = (chain: IDocHeading[], level: number) => chain.filter(heading => heading.level <= level).at(-1)
    const content = pieces.filter(piece => piece.blocks.some(block => block.type !== 'heading'))
    const first = opening(content[0] || pieces[0]!)
    const last = opening(content.at(-1) || pieces.at(-1)!)
    for (const level of [1, 2, 3]) {
        const a = at(first, level)
        const b = at(last, level)
        if (a === b) continue
        const parent = level === 3 && at(first, 2) === at(last, 2) ? `${name(at(first, 2))}: ` : ''
        return `${parent}${name(a)} – ${name(b)}`
    }
    const own = at(first, 3)
    const parent = at(first, 2)
    const started = !!own && !pieces.some(piece => piece.blocks.includes(own))
    const prefix = parent && parent !== own && parent.level > 1 ? `${name(parent)}: ` : ''
    return `${prefix}${name(own)}${started ? ' (continued)' : ''}`
}

// The same pieces in at least two parts, with a budget scaled to the written size, halved until they divide.
function smaller(pieces: IDocPiece[], estimate: number, written: number, format: TExportFormat): IDocPiece[][] {
    let budget = estimate * (LIMIT / written) * 0.8
    for (let tries = 0; tries < 10; tries++) {
        const parts = packPieces(pieces, format, budget)
        if (parts.length > 1) return parts
        budget /= 2
    }
    throw new Error('A section of the document is too large for one download and cannot be divided.')
}

// Writes a document as one file, or, when that would exceed the limit, as parts at letters, roots, texts or
// smaller sections. Every part is written and measured; one still over the limit (text that compresses badly
// can be several times its estimate) is divided again with a budget scaled by how far the estimate fell short.
export async function planDocument(
    doc: IExportDocument,
    format: TExportFormat,
    write: (doc: IExportDocument) => Promise<Buffer>
): Promise<IPlannedPart[]> {
    const whole: IDocPiece = {
        context: [],
        blocks: doc.blocks,
    }
    let pending = packPieces([whole], format, TARGET - estimateSize([], format))
    if (pending.length === 1) {
        const bytes = await write(doc)
        if (bytes.length <= LIMIT) return [{
            part: 1,
            label: '',
            fileName: `${doc.fileName}.${format}`,
            bytes,
        }]
        pending = smaller([whole], variable(doc.blocks, format), bytes.length, format)
    }
    const parts: IPlannedPart[] = []
    while (pending.length) {
        const pieces = pending.shift()!
        const n = parts.length + 1
        const partLabel = label(pieces)
        const blocks = assemblePart(pieces)
        const part: IExportDocument = {
            ...doc,
            fileName: `${doc.fileName}-part-${n}`,
            front: [
                ...doc.front.slice(0, 2),
                {
                    type: 'paragraph',
                    style: 'meta',
                    runs: [{
                        text: `Part ${n}: ${partLabel}. The document comes in several parts, downloaded separately; `
                            + 'links to sections in other parts are plain text here.',
                    }],
                },
                ...doc.front.slice(2),
            ],
            blocks,
        }
        const bytes = await write(part)
        if (bytes.length <= LIMIT) parts.push({
            part: n,
            label: partLabel,
            fileName: `${part.fileName}.${format}`,
            bytes,
        })
        else pending.unshift(...smaller(pieces, variable(blocks, format), bytes.length, format))
    }
    return parts
}
