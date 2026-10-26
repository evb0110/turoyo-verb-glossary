import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { readGlossaryAsset } from '~~/server/repositories/glossary/readGlossaryAsset'
import type { IEntry } from '#shared/types/IEntry'

export async function getEntry(id: string): Promise<IEntry | null> {
    if (!(await getEntryIndex()).some(row => row.id === id)) return null
    return await readGlossaryAsset<IEntry>(`entries/${id}.json`)
}
