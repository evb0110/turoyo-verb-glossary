import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import type { IEntry } from '#shared/types/IEntry'

export async function getEntry(id: string): Promise<IEntry | null> {
    return (await getGlossaryCatalog()).entries.find(entry => entry.id === id) || null
}
