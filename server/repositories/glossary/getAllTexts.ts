import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import { getText } from '~~/server/repositories/glossary/getText'
import { getTextIndex } from '~~/server/repositories/glossary/getTextIndex'
import type { IText } from '#shared/types/IText'

// Every corpus text (over 100 MB): only full-text search and the research notes need them all.
export const getAllTexts = cachedAsset(async () =>
    (await Promise.all((await getTextIndex()).map(row => getText(row.id))))
        .filter((text): text is IText => text !== null))
