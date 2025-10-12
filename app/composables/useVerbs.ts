import type { Verb, VerbIndex, VerbIndexEntry, Statistics, CrossReferences } from '~/types/verb'
import { rootToSlug, slugToRoot } from '~/utils/slugify'

/**
 * Composable for working with Turoyo verb data
 * Provides efficient loading and access to verb information
 */
export const useVerbs = () => {
    // State management for cached data
    // NOTE: index is NOT in useState to avoid serializing 540KB of data into HTML
    // Only statistics and cross-refs need to be shared state
    const statistics = useState<Statistics | null>('statistics', () => null)
    const crossRefs = useState<CrossReferences | null>('cross-refs', () => null)

    // Local cache for index (not shared state)
    let indexCache: VerbIndex | null = null

    /**
   * Load the verb index from server API
   * @deprecated No longer needed! Search now returns metadata directly.
   * This function loads 540KB of data and is kept only for backward compatibility.
   */
    const loadIndex = async (): Promise<VerbIndex> => {
        console.warn('[useVerbs] loadIndex is deprecated - search now returns metadata directly')

        if (indexCache) {
            return indexCache
        }

        const data = await $fetch<{ total: number, verbs: VerbIndexEntry[] }>('/api/verbs')

        indexCache = {
            version: '1.0',
            last_updated: new Date().toISOString(),
            total_verbs: data.total,
            roots: data.verbs
        }

        return indexCache
    }

    /**
   * Load statistics from server API
   * Uses useAsyncData for SSR hydration
   */
    const loadStatistics = async (): Promise<Statistics> => {
        const { data } = await useAsyncData('statistics', () =>
            $fetch<Statistics>('/api/stats')
        )

        if (data.value) {
            statistics.value = data.value
        }

        return statistics.value as Statistics
    }

    /**
   * Load cross-references mapping (from static file generated at build time)
   */
    const loadCrossReferences = async (): Promise<CrossReferences> => {
        if (!crossRefs.value) {
            // Cross-refs are built at build time and served as static JSON
            crossRefs.value = await $fetch<CrossReferences>('/api/cross-refs')
        }
        return crossRefs.value as CrossReferences
    }

    /**
   * Get a single verb by root (lazy loaded, ~2-5KB per verb)
   * @param root - The root of the verb to fetch
   */
    const getVerb = async (root: string): Promise<Verb> => {
        // URL-encode the root to handle Unicode characters (ṣ, š, ǧ, etc.)
        const encodedRoot = encodeURIComponent(root)
        // Use API endpoint that serves from server assets (works in SSR and client)
        return await $fetch<Verb>(`/api/verbs/${encodedRoot}`)
    }

    /**
   * Get a verb following cross-references if needed
   * @param root - The root to look up
   */
    const getVerbWithCrossRef = async (rootOrSlug: string): Promise<Verb> => {
        const canonicalRoot = slugToRoot(rootOrSlug)
        const refs = await loadCrossReferences()
        const targetRoot = refs[canonicalRoot] || canonicalRoot
        return await getVerb(targetRoot)
    }

    return {
    // Data loading
        loadIndex,
        loadStatistics,
        loadCrossReferences,

        // Slugs
        rootToSlug,
        slugToRoot,

        // Single verb access
        getVerb,
        getVerbWithCrossRef,

        // State access (for direct use if needed)
        statistics: readonly(statistics),
        crossRefs: readonly(crossRefs)
    }
}
