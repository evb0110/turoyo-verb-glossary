import type { IDocRun } from '~~/server/types/export/IDocRun'
import type { TDocParagraphStyle } from '~~/server/types/export/TDocParagraphStyle'

export interface IDocParagraph {
    type: 'paragraph'
    style: TDocParagraphStyle
    runs: IDocRun[]
}
