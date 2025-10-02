// Type definitions for Turoyo Verb data structures

export interface Etymology {
  source: string
  source_root?: string
  reference?: string
  meaning?: string
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
  binyan?: string
  label_raw?: string
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
  etymology_source: string | null
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

export interface SearchIndex {
  turoyo_index: { [key: string]: string[] }
  translation_index: { [key: string]: string[] }
  etymology_index: { [key: string]: string[] }
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
  // State management for cached data
  const index = useState<VerbIndex | null>('verbs-index', () => null)
  const searchIndex = useState<SearchIndex | null>('search-index', () => null)
  const statistics = useState<Statistics | null>('statistics', () => null)
  const crossRefs = useState<CrossReferences | null>('cross-refs', () => null)

  /**
   * Load the verb index (lightweight, ~100KB)
   * Call this once on app initialization
   */
  const loadIndex = async (): Promise<VerbIndex> => {
    if (!index.value) {
      index.value = await $fetch('/data/api/index.json')
    }
    return index.value
  }

  /**
   * Load the search index (optimized for search, ~500KB)
   * Call this on first search or load on demand
   */
  const loadSearchIndex = async (): Promise<SearchIndex> => {
    if (!searchIndex.value) {
      try {
        console.log('[useVerbs] Loading search index...')
        searchIndex.value = await $fetch('/data/api/search.json')
        console.log('[useVerbs] Search index loaded:', {
          turoyo_keys: Object.keys(searchIndex.value.turoyo_index).length,
          translation_keys: Object.keys(searchIndex.value.translation_index).length,
          etymology_keys: Object.keys(searchIndex.value.etymology_index).length
        })
      } catch (error) {
        console.error('[useVerbs] Failed to load search index:', error)
        throw error
      }
    }
    return searchIndex.value
  }

  /**
   * Load statistics data
   */
  const loadStatistics = async (): Promise<Statistics> => {
    if (!statistics.value) {
      statistics.value = await $fetch('/data/api/statistics.json')
    }
    return statistics.value
  }

  /**
   * Load cross-references mapping
   */
  const loadCrossReferences = async (): Promise<CrossReferences> => {
    if (!crossRefs.value) {
      crossRefs.value = await $fetch('/data/api/cross-refs.json')
    }
    return crossRefs.value
  }

  /**
   * Get a single verb by root (lazy loaded, ~2-5KB per verb)
   * @param root - The root of the verb to fetch
   */
  const getVerb = async (root: string): Promise<Verb> => {
    return await $fetch(`/data/api/verbs/${root}.json`)
  }

  /**
   * Get a verb following cross-references if needed
   * @param root - The root to look up
   */
  const getVerbWithCrossRef = async (root: string): Promise<Verb> => {
    const refs = await loadCrossReferences()
    const targetRoot = refs[root] || root
    return await getVerb(targetRoot)
  }

  /**
   * Search for verbs matching a query
   * Searches across Turoyo forms, translations, and etymology
   * @param query - Search query string
   * @param options - Search options
   */
  const search = async (
    query: string,
    options: {
      searchTuroyo?: boolean
      searchTranslations?: boolean
      searchEtymology?: boolean
      maxResults?: number
    } = {}
  ): Promise<string[]> => {
    const {
      searchTuroyo = true,
      searchTranslations = true,
      searchEtymology = true,
      maxResults = 100
    } = options

    console.log('[useVerbs] Search called with query:', query, 'options:', options)

    const idx = await loadSearchIndex()
    const roots = new Set<string>()
    const lowerQuery = query.toLowerCase()

    // Search in Turoyo index
    if (searchTuroyo) {
      for (const [word, verbRoots] of Object.entries(idx.turoyo_index)) {
        if (word.toLowerCase().includes(lowerQuery)) {
          verbRoots.forEach(r => roots.add(r))
        }
      }
    }

    // Search in translation index
    if (searchTranslations) {
      for (const [word, verbRoots] of Object.entries(idx.translation_index)) {
        if (word.toLowerCase().includes(lowerQuery)) {
          verbRoots.forEach(r => roots.add(r))
        }
      }
    }

    // Search in etymology index
    if (searchEtymology) {
      for (const [source, verbRoots] of Object.entries(idx.etymology_index)) {
        if (source.toLowerCase().includes(lowerQuery)) {
          verbRoots.forEach(r => roots.add(r))
        }
      }
    }

    const results = Array.from(roots)
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
    const idx = await loadSearchIndex()
    return idx.etymology_index[source] || []
  }

  /**
   * Get verbs by stem
   * @param stem - Stem name (e.g., "I", "II", "III", "Detransitive")
   */
  const getVerbsByStem = async (stem: string): Promise<VerbIndexEntry[]> => {
    const idx = await loadIndex()
    return idx.roots.filter(r => r.stems.includes(stem))
  }

  /**
   * Get all verbs starting with a specific letter
   * @param letter - First letter of the root
   */
  const getVerbsByLetter = async (letter: string): Promise<VerbIndexEntry[]> => {
    const idx = await loadIndex()
    return idx.roots.filter(r => r.root.startsWith(letter))
  }

  return {
    // Data loading
    loadIndex,
    loadSearchIndex,
    loadStatistics,
    loadCrossReferences,

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
    searchIndex: readonly(searchIndex),
    statistics: readonly(statistics),
    crossRefs: readonly(crossRefs)
  }
}
