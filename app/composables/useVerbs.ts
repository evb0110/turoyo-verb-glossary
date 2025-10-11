import type { Verb, VerbIndex, VerbIndexEntry, Statistics, CrossReferences } from '~/types/verb'
import { rootToSlug, slugToRoot } from '~/utils/slugify'

/**
 * Composable for working with Turoyo verb data
 * Provides efficient loading and access to verb information
 */
export const useVerbs = () => {
    // State management for cached data
    const index = useState<VerbIndex | null>('verbs-index', () => null)
    const statistics = useState<Statistics | null>('statistics', () => null)
    const crossRefs = useState<CrossReferences | null>('cross-refs', () => null)

    /**
   * Load the verb index from server API
   * Uses useAsyncData for SSR hydration
   */
    const loadIndex = async (): Promise<VerbIndex> => {
        const { data } = await useAsyncData('verbs-index', () =>
            $fetch<{ total: number, verbs: VerbIndexEntry[] }>('/api/verbs')
        )

        if (data.value) {
            index.value = {
                version: '1.0',
                last_updated: new Date().toISOString(),
                total_verbs: data.value.total,
                roots: data.value.verbs
            }
        }

        return index.value as VerbIndex
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
   * Load cross-references mapping (generated from verb files)
   */
    const loadCrossReferences = async (): Promise<CrossReferences> => {
        if (!crossRefs.value) {
            // Cross-refs are now built dynamically from verb files
            // We get them from the server index which loads all verbs
            await loadIndex()
            // The cross-refs are built server-side during loadAllVerbs()
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
        index: readonly(index),
        statistics: readonly(statistics),
        crossRefs: readonly(crossRefs)
    }
}
