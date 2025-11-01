import { generateVerbMetadata } from '~~/server/services/generateVerbMetadata'
import type { IRootsSearchResult } from '~~/server/types/IRootsSearchResult'
import type { ISearchOptions } from '~~/server/types/ISearchOptions'
import { matchesPattern } from '~~/server/utils/matchesPattern'
import type { IVerb } from '#shared/types/IVerb'
import type { IVerbMetadataWithPreview } from '#shared/types/IVerbMetadataWithPreview'

export async function searchRoots(
    query: string,
    opts: ISearchOptions
): Promise<IRootsSearchResult> {
    const storage = useStorage('assets:server')
    const matchingRoots: string[] = []
    const verbMetadata: Record<string, IVerbMetadataWithPreview> = {}

    const allFiles = await storage.getKeys('verbs')
    const verbFiles = allFiles.filter(f => f.endsWith('.json'))

    const allRoots = verbFiles.map(f => {
        const match = f.match(/verbs[:/](.+)\.json$/)
        return match ? match[1] : null
    }).filter((r): r is string => r !== null)

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
                if (!verb) {
                    return null
                }

                const metadata = generateVerbMetadata(verb, 'roots', '', opts)
                verbMetadata[root] = metadata

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
