import { getEntry } from '~~/server/repositories/glossary/getEntry'
import type { IEntry } from '#shared/types/IEntry'

// The entries with these ids, in the same order; unknown ids are left out.
export async function getEntries(ids: string[]): Promise<IEntry[]> {
    return (await Promise.all(ids.map(id => getEntry(id)))).filter((entry): entry is IEntry => entry !== null)
}
