import type { IDocParagraph } from '~~/server/types/export/IDocParagraph'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'

// One scope of the site as a format-neutral document; renderDocx and renderPdf write it.
export interface IExportDocument {
    fileName: string // without extension, may contain Turoyo letters
    title: string
    subject: string
    keywords: string[]
    front: IDocParagraph[] // the title block
    contentsDepth: 0 | 1 | 2 | 3 // heading levels in the table of contents; 0 for none
    headerLevel: 0 | 1 | 2 // the heading level shown in the running header beside the title; 0 for the title only
    blocks: TDocBlock[]
}
