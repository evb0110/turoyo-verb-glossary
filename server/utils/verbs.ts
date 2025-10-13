// NOTE: search-index.json has been eliminated - search is now done at runtime
// See server/api/verbs-fulltext-search.post.ts for the runtime search implementation
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

/**
 * DEPRECATED: Search index has been removed in favor of runtime search
 * Use /api/verbs-fulltext-search instead for search functionality
 *
 * This interface is kept for backward compatibility but should not be used
 */
interface SearchIndex {
    verbs?: Array<{
        root: string
        etymology_sources: string[]
        stems: string[]
        forms: string[]
        example_count: number
    }>
}

/**
 * DEPRECATED: Static search index has been eliminated
 * Use server/api/verbs-fulltext-search.post.ts for runtime search instead
 *
 * @deprecated This function will throw an error
 */
export async function loadSearchIndex(): Promise<SearchIndex> {
    throw new Error(
        'loadSearchIndex() is deprecated. Static search index has been eliminated. ' +
        'Use /api/verbs-fulltext-search for runtime search instead.'
    )
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
