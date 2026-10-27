import { estimateSize } from '~~/server/services/export/estimateSize'
import { headingChain } from '~~/server/services/export/headingChain'
import type { IDocPiece } from '~~/server/types/export/IDocPiece'
import type { IDocVerseTable } from '~~/server/types/export/IDocVerseTable'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'
import type { TExportFormat } from '~~/server/types/export/TExportFormat'

function size(blocks: TDocBlock[], format: TExportFormat) {
    return estimateSize(blocks, format) - estimateSize([], format)
}

// Consecutive items in the fewest runs of about equal size that keep under the budget (at least one item each).
function runs<T>(items: T[], measure: (item: T) => number, budget: number): T[][] {
    const sizes = items.map(measure)
    const total = sizes.reduce((sum, value) => sum + value, 0)
    const count = Math.max(1, Math.ceil(total / budget))
    const result: T[][] = [[]]
    let filled = 0
    items.forEach((item, n) => {
        const itemSize = sizes[n]!
        const full = result.length < count && filled + itemSize / 2 > total / count
        if (result.at(-1)!.length && (full || filled + itemSize > budget)) {
            result.push([])
            filled = 0
        }
        result.at(-1)!.push(item)
        filled += itemSize
    })
    return result
}

// A piece over the budget is divided at its outermost inner headings (letters, then roots, stems, meanings or
// single decisions); a piece without inner headings into runs of paragraphs, and a verse table into runs of
// verses. Every smaller piece keeps the headings it sits under.
function expand(piece: IDocPiece, format: TExportFormat, budget: number): IDocPiece[] {
    if (size(piece.blocks, format) <= budget) return [piece]
    const inner = piece.blocks.slice(1).filter(block => block.type === 'heading')
    if (inner.length) {
        const level = Math.min(...inner.map(heading => heading.level))
        const cuts = [0, ...piece.blocks.flatMap((block, n) =>
            n > 0 && block.type === 'heading' && block.level === level ? [n] : []), piece.blocks.length]
        return cuts.slice(0, -1).flatMap((start, n) => expand({
            context: start
                ? headingChain(piece.context, piece.blocks.slice(0, start)).filter(heading => heading.level < level)
                : piece.context,
            blocks: piece.blocks.slice(start, cuts[n + 1]),
        }, format, budget))
    }
    const lead = piece.blocks.findIndex(block => block.type !== 'heading')
    if (lead < 0) return [piece]
    const heads = piece.blocks.slice(0, lead)
    const items = piece.blocks.slice(lead)
    const table = items.length === 1 && items[0]!.type === 'verses' ? items[0] as IDocVerseTable : null
    const groups: TDocBlock[][] = table
        ? runs(table.rows, row => size([{
                ...table,
                rows: [row],
            }], format), budget).map(rows => [{
                ...table,
                rows,
            }])
        : runs(items, item => size([item], format), budget)
    if (groups.length < 2) return [piece]
    const under = headingChain(piece.context, heads)
    return groups.flatMap((group, n) => expand(n
        ? {
                context: under,
                blocks: group,
            }
        : {
                context: piece.context,
                blocks: [...heads, ...group],
            }, format, budget))
}

// Divides the pieces as finely as the budget needs, then packs them, in order, into the fewest parts of about
// equal estimated size that keep under it.
export function packPieces(pieces: IDocPiece[], format: TExportFormat, budget: number): IDocPiece[][] {
    return runs(pieces.flatMap(piece => expand(piece, format, budget)), unit => size(unit.blocks, format), budget)
}
