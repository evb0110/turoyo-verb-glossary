import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import { getAllTexts } from '~~/server/repositories/glossary/getAllTexts'
import { getEntry } from '~~/server/repositories/glossary/getEntry'
import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { buildSearchIndex } from '~~/server/services/glossary/buildSearchIndex'
import type { IEntry } from '#shared/types/IEntry'

export const getSearchIndex = cachedAsset(async () => {
    const entries = (await Promise.all((await getEntryIndex()).map(row => getEntry(row.id))))
        .filter((entry): entry is IEntry => entry !== null)
    return buildSearchIndex(entries, await getAllTexts())
})
