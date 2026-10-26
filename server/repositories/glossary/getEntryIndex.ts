import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import type { IEntryIndex } from '#shared/types/IEntryIndex'

export const getEntryIndex = cachedAsset(async () =>
    (await readGlossaryAsset<IEntryIndex[]>('index.json'))
    || (await readGlossaryAsset<IEntryIndex[]>('entries/index.json'))
    || [])
