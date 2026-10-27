import type { IDocHeading } from '~~/server/types/export/IDocHeading'
import type { IDocParagraph } from '~~/server/types/export/IDocParagraph'
import type { IDocVerseTable } from '~~/server/types/export/IDocVerseTable'

export type TDocBlock = IDocHeading | IDocParagraph | IDocVerseTable
