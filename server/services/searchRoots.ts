import type { IVerb } from '~/types/IVerb'
import type { IVerbMetadata } from '~/types/IVerbMetadata'
import type { ISearchOptions } from '~~/server/services/ISearchOptions'
import type { IRootsSearchResult } from '~~/server/services/IRootsSearchResult'
import { matchesPattern } from '~~/server/utils/matchesPattern'
import { extractMetadata } from '~~/server/services/extractMetadata'

export async function searchRoots(
    allRoots: string[],
    query: string,
    opts: ISearchOptions
): Promise<IRootsSearchResult> {
    const storage = useStorage('assets:server')
    const matchingRoots: string[] = []
    const verbPreviews: Record<string, { verb?: IVerb }> = {}
    const verbMetadata: Record<string, IVerbMetadata> = {}

    const filteredRoots = allRoots.filter(root =>
        matchesPattern(root, query, opts)
    )

    console.log(`[Verb Search] Found ${filteredRoots.length} matching roots`)

    const BATCH_SIZE = 50
    for (let i = 0; i < filteredRoots.length; i += BATCH_SIZE) {
        const batch = filteredRoots.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (root: string) => {
            try {
                const verb = await storage.getItem<IVerb>(`verbs/${root}.json`)
                if (!verb) return null

                verbPreviews[root] = { verb }
                verbMetadata[root] = extractMetadata(verb)

                return root
            }
            catch (e) {
                console.warn(`[Verb Search] Failed to load ${root}:`, e)
                return null
            }
        })

        const batchResults = await Promise.all(batchPromises)
        matchingRoots.push(...batchResults.filter((r): r is string => r !== null))
    }

    return {
        total: matchingRoots.length,
        roots: matchingRoots,
        verbPreviews,
        verbMetadata
    }
}
