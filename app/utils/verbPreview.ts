/**
 * Verb preview utilities for loading and displaying verb data
 */

import type { Verb, VerbIndexEntry } from '~/types/verb'

/**
 * Batch load full verb data for search results
 * Loads all verbs in parallel for best performance
 *
 * @param results - Array of verb index entries to load
 * @returns Map of root names to full verb data
 *
 * @example
 * const verbMap = await loadVerbsForResults(searchResults)
 * const verb = verbMap.get('ʕbd')
 */
export async function loadVerbsForResults(
    results: VerbIndexEntry[]
): Promise<Map<string, Verb>> {
    const { getVerb } = useVerbs()
    const verbMap = new Map<string, Verb>()

    console.log(`[verbPreview] Loading ${results.length} verbs...`)

    // Load all in parallel
    await Promise.all(
        results.map(async (entry) => {
            try {
                const verb = await getVerb(entry.root)
                verbMap.set(entry.root, verb)
            }
            catch (e) {
                console.warn(`[verbPreview] Failed to load verb ${entry.root}:`, e)
            }
        })
    )

    console.log(`[verbPreview] Loaded ${verbMap.size} verbs successfully`)
    return verbMap
}
