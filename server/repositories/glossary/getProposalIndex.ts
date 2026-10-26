import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import type { IProposalIndex } from '#shared/types/IProposalIndex'

export const getProposalIndex = cachedAsset(async () =>
    (await readGlossaryAsset<IProposalIndex[]>('proposals/index.json')) || [])
