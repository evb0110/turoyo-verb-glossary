import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import type { ITextIndex } from '#shared/types/ITextIndex'
import { textHeading } from '#shared/utils/textHeading'

type TTextIndexRow = Omit<ITextIndex, 'reading' | 'occurrenceCount'> & {
    reading?: ITextIndex['reading']
    occurrences?: number
}

export const getTextIndex = cachedAsset(async (): Promise<ITextIndex[]> =>
    ((await readGlossaryAsset<TTextIndexRow[]>('texts/index.json')) || []).map(({
        occurrences,
        ...row
    }) => ({
        ...row,
        ...textHeading(row.title, row.cite),
        reading: row.reading || 'unread',
        occurrenceCount: occurrences || 0,
    })))
