// Type definitions for Turoyo Verb data structures

export interface Etymon {
    source: string
    source_root?: string
    reference?: string
    meaning?: string
    stem?: string // I, II, III, IV, Pa., Af., etc.
    raw?: string
}

export interface Etymology {
    etymons: Etymon[]
    relationship?: 'also' | 'or' | 'and'
}

export interface Example {
    turoyo: string
    translations: string[]
    references: string[]
}

export interface Stem {
    stem: string
    forms: string[]
    conjugations: {
        [key: string]: Example[]
    }
    // Optional fields from parser
    label_raw?: string
    label_gloss_tokens?: { italic: boolean, text: string }[]
}

export interface Verb {
    root: string
    etymology: Etymology | null
    cross_reference: string | null
    stems: Stem[]
    uncertain: boolean
    // Optional raw header HTML preserved verbatim
    lemma_header_raw?: string
}

export interface VerbIndexEntry {
    root: string
    etymology_sources: string[]
    stems: string[]
    has_detransitive: boolean
    cross_reference: string | null
    example_count: number
    forms: string[]
}

export interface VerbIndex {
    version: string
    total_verbs: number
    last_updated: string
    roots: VerbIndexEntry[]
}

export interface Statistics {
    total_verbs: number
    total_stems: number
    total_examples: number
    by_etymology: { [key: string]: number }
    by_stem: { [key: string]: number }
    by_letter: { [key: string]: number }
}

export interface CrossReferences {
    [key: string]: string
}

/**
 * Composable for working with Turoyo verb data
 * Provides efficient loading and searching of verb information
 */
export const useVerbs = () => {
    async function readPublicJson<T>(path: string): Promise<T> {
        const normalized = path.startsWith('/') ? path : `/${path}`
        // On server: use internal API (Nitro assets storage)
        if (import.meta.server) {
            const withoutLeading = normalized.slice(1)
            const apiRelative = withoutLeading.startsWith('appdata/api/')
                ? withoutLeading.slice('appdata/api/'.length)
                : withoutLeading
            const apiUrl = `/api/data/${apiRelative}`
            // On Vercel, prefer absolute fetch from the deployment origin to bypass any server route issues
            const vercelHost = process.env.VERCEL_URL
            if (vercelHost) {
                try {
                    const absolute = `https://${vercelHost}${normalized}`
                    return await $fetch<T>(absolute)
                }
                catch {
                    // fall through to internal API
                }
            }
            try {
                return await $fetch<T>(apiUrl)
            }
            catch {
                // Fallback to static path if route is unavailable
                return await $fetch<T>(normalized)
            }
        }
        // On client: fetch directly from the CDN/static public path
        return await $fetch<T>(normalized)
    }
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

    // Slug helpers for homonymous roots (e.g., "bdy 1" → "bdy-1")
    const rootToSlug = (root: string) => root.replace(/\s+/g, '-')
    const slugToRoot = (slug: string) => slug.replace(/-/g, ' ')

    /**
   * Get a single verb by root (lazy loaded, ~2-5KB per verb)
   * @param root - The root of the verb to fetch
   */
    const getVerb = async (root: string): Promise<Verb> => {
        return await readPublicJson<Verb>(`appdata/api/verbs/${root}.json`)
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

    /**
   * Search for verbs matching a query
   * Uses server API to search across all verb data
   * @param query - Search query string
   * @param options - Search options
   */
    const search = async (
        query: string,
        options: {
            rootsOnly?: boolean
            searchTranslations?: boolean
            maxResults?: number
            useRegex?: boolean
        } = {}
    ): Promise<string[]> => {
        const {
            rootsOnly = false,
            searchTranslations = false,
            maxResults,
            useRegex = false
        } = options

        console.log('[useVerbs] Search called with query:', query, 'options:', options)

        // Build query params for server API
        const params: Record<string, string> = {
            q: query
        }

        if (rootsOnly) {
            params.rootsOnly = 'true'
        }

        if (searchTranslations) {
            params.searchTranslations = 'true'
        }

        if (useRegex) {
            params.useRegex = 'true'
        }

        // Use useAsyncData with dynamic key based on query
        const cacheKey = `search-${query}-${rootsOnly ? 'roots' : 'all'}-${searchTranslations ? 'trans' : 'notrans'}-${useRegex ? 'regex' : 'plain'}`
        const { data } = await useAsyncData(
            cacheKey,
            () => $fetch<{ total: number, verbs: VerbIndexEntry[] }>('/api/verbs', {
                query: params
            })
        )

        if (!data.value) {
            return []
        }

        const results = data.value.verbs.map(v => v.root)
        console.log('[useVerbs] Search found', results.length, 'total results')
        const final = maxResults ? results.slice(0, maxResults) : results
        console.log('[useVerbs] Returning', final.length, 'results (after maxResults filter)')
        return final
    }

    /**
   * Get all verbs by etymology source
   * @param source - Etymology source (e.g., "Arab.", "MA", "Kurd.")
   */
    const getVerbsByEtymology = async (source: string): Promise<string[]> => {
        const { data } = await useAsyncData(
            `etymology-${source}`,
            () => $fetch<{ total: number, verbs: VerbIndexEntry[] }>('/api/verbs', {
                query: { etymology: source }
            })
        )

        return data.value?.verbs.map(v => v.root) || []
    }

    /**
   * Get verbs by stem
   * @param stem - Stem name (e.g., "I", "II", "III", "Detransitive")
   */
    const getVerbsByStem = async (stem: string): Promise<VerbIndexEntry[]> => {
        const { data } = await useAsyncData(
            `stem-${stem}`,
            () => $fetch<{ total: number, verbs: VerbIndexEntry[] }>('/api/verbs', {
                query: { stem }
            })
        )

        return data.value?.verbs || []
    }

    /**
   * Get all verbs starting with a specific letter
   * @param letter - First letter of the root
   */
    const getVerbsByLetter = async (letter: string): Promise<VerbIndexEntry[]> => {
        const { data } = await useAsyncData(
            `letter-${letter}`,
            () => $fetch<{ total: number, verbs: VerbIndexEntry[] }>('/api/verbs', {
                query: { letter }
            })
        )

        return data.value?.verbs || []
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

        // Search and filtering
        search,
        getVerbsByEtymology,
        getVerbsByStem,
        getVerbsByLetter,

        // State access (for direct use if needed)
        index: readonly(index),
        statistics: readonly(statistics),
        crossRefs: readonly(crossRefs)
    }
}
