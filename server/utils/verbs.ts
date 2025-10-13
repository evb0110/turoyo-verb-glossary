import searchIndexData from '../../public/appdata/api/search-index.json'
import crossRefsData from '../../public/appdata/api/cross-refs.json'
import statsData from '../../public/appdata/api/stats.json'

export interface Verb {
    root: string
    etymology: {
        etymons: Array<{
            source: string
            source_root?: string
            reference?: string
            meaning?: string
            notes?: string
            stem?: string
            raw?: string
        }>
        relationship?: 'also' | 'or' | 'and'
    } | null
    cross_reference: string | null
    stems: Array<{
        stem?: string
        forms: string[]
        conjugations: Record<string, Array<{
            turoyo: string
            translations: string[]
            references: string[]
        }>>
        label_raw?: string
        label_gloss_tokens?: Array<{ italic: boolean, text: string }>
    }>
    uncertain: boolean
    lemma_header_raw?: string
    lemma_header_tokens?: Array<{ italic: boolean, text: string }>
}

interface SearchIndex {
    verbs?: Array<{
        root: string
        etymology_sources: string[]
        stems: string[]
        forms: string[]
        example_count: number
    }>
}

// Search index cache (lightweight, loaded from static file)
let searchIndexCache: SearchIndex | null = null

/**
 * Load search index (lightweight, single file)
 * Used for fast filtering/search operations
 */
export async function loadSearchIndex(): Promise<SearchIndex> {
    if (!searchIndexCache) {
    // Use imported JSON data (bundled at build time)
        searchIndexCache = searchIndexData as SearchIndex
        console.log(`[loadSearchIndex] Loaded search index with ${searchIndexCache?.verbs?.length || 0} verbs`)
    }
    return searchIndexCache
}

/**
 * Get cross-references mapping (from static file)
 */
export async function getCrossReferences(): Promise<Record<string, string>> {
    // Use imported JSON data (bundled at build time)
    return crossRefsData as Record<string, string>
}

/**
 * Get pre-computed statistics (generated at build time)
 */
export function getStatistics() {
    // Use imported JSON data (bundled at build time)
    return statsData
}

/**
 * Clear the search index cache (useful for development)
 */
export function clearSearchIndexCache() {
    searchIndexCache = null
}
