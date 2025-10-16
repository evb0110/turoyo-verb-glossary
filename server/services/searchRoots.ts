import type { IVerb } from '~/types/IVerb'
import { extractMetadata } from '~~/server/services/extractMetadata'
import type { IRootsSearchResult } from '~~/server/types/IRootsSearchResult'
import type { ISearchOptions } from '~~/server/types/ISearchOptions'
import type { IVerbMetadataWithPreview } from '~~/server/types/IVerbMetadataWithPreview'
import { matchesPattern } from '~~/server/utils/matchesPattern'

export async function searchRoots(
    allRoots: string[],
    query: string,
    opts: ISearchOptions
): Promise<IRootsSearchResult> {
    const storage = useStorage('assets:server')
    const matchingRoots: string[] = []
    const verbMetadata: Record<string, IVerbMetadataWithPreview> = {}

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
                if (!verb)
                    return null

                const metadata = extractMetadata(verb)
                verbMetadata[root] = {
                    ...metadata,
                    verbPreview: verb,
                }

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
        verbMetadata,
    }
}
