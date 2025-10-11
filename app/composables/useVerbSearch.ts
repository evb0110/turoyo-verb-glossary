import type { VerbIndexEntry } from '~/types/verb'

/**
 * Composable for searching and filtering Turoyo verbs
 * Provides search functionality across roots, forms, translations, and etymology
 */
export const useVerbSearch = () => {
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
            caseSensitive?: boolean
        } = {}
    ): Promise<string[]> => {
        const {
            rootsOnly = false,
            searchTranslations = false,
            maxResults,
            useRegex = false,
            caseSensitive = false
        } = options

        console.log('[useVerbSearch] Search called with query:', query, 'options:', options)

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

        if (caseSensitive) {
            params.caseSensitive = 'true'
        }

        // Use useAsyncData with dynamic key based on query
        const cacheKey = `search-${query}-${rootsOnly ? 'roots' : 'all'}-${searchTranslations ? 'trans' : 'notrans'}-${useRegex ? 'regex' : 'plain'}-${caseSensitive ? 'cs' : 'ci'}`
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
        console.log('[useVerbSearch] Search found', results.length, 'total results')
        const final = maxResults ? results.slice(0, maxResults) : results
        console.log('[useVerbSearch] Returning', final.length, 'results (after maxResults filter)')
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
        search,
        getVerbsByEtymology,
        getVerbsByStem,
        getVerbsByLetter
    }
}
