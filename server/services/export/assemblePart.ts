import { headingChain } from '~~/server/services/export/headingChain'
import type { IDocHeading } from '~~/server/types/export/IDocHeading'
import type { IDocPiece } from '~~/server/types/export/IDocPiece'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'

// The blocks of one part. Where a piece starts inside a section whose heading is not already in the part,
// that heading is repeated, marked "(continued)", so the part keeps its letter > root > stem structure.
export function assemblePart(pieces: IDocPiece[]): TDocBlock[] {
    const blocks: TDocBlock[] = []
    let open: IDocHeading[] = []
    for (const piece of pieces) {
        let same = 0
        while (same < open.length && same < piece.context.length && open[same] === piece.context[same]) same++
        open = open.slice(0, same)
        for (const heading of piece.context.slice(same)) {
            blocks.push({
                ...heading,
                id: `${heading.id}~continued`,
                runs: [...heading.runs, { text: ' (continued)' }],
            })
            open.push(heading)
        }
        blocks.push(...piece.blocks)
        open = headingChain(open, piece.blocks)
    }
    return blocks
}
