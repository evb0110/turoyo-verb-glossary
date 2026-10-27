import type { IDocHeading } from '~~/server/types/export/IDocHeading'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'

// A run of consecutive blocks of a document, with the headings it sits under (outermost first). A part that
// starts inside a section repeats those headings, marked "(continued)".
export interface IDocPiece {
    context: IDocHeading[]
    blocks: TDocBlock[]
}
