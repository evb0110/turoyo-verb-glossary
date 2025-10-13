import searchIndexData from '../../public/appdata/api/search-index.json'
import crossRefsData from '../../public/appdata/api/cross-refs.json'
import verbsManifest from '../../public/appdata/api/verbs-manifest.json'
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

// Full verbs cache (heavy, only loaded when needed for stats)
let verbsCache: Verb[] | null = null
let verbsCacheTime: number = 0
const CACHE_TTL = 3600000 // 1 hour cache

/**
 * Load all verb files from public/appdata/api/verbs/
 * Aggressively cached (1 hour) for serverless performance
 */
export async function loadAllVerbs(): Promise<Verb[]> {
    const now = Date.now()

    // Return cached data if still fresh
    if (verbsCache && (now - verbsCacheTime) < CACHE_TTL) {
        console.log(`[loadAllVerbs] Using cached verbs (${verbsCache.length} verbs)`)
        return verbsCache
    }

    console.log('[loadAllVerbs] Cache miss or expired, loading verbs...')

    try {
    // Use imported manifest (bundled at build time)
        const manifest = verbsManifest as string[]

        if (!manifest || !Array.isArray(manifest)) {
            throw new Error('Invalid manifest format')
        }

        console.log(`[loadAllVerbs] Loading ${manifest.length} verbs from manifest`)

        // Read individual verb files from storage
        const storage = useStorage('assets:public')

        // Load verbs in batches to avoid timeout
        const verbs: Verb[] = []
        const BATCH_SIZE = 50
        const crossRefs: Record<string, string> = {}

        for (let i = 0; i < manifest.length; i += BATCH_SIZE) {
            const batch = manifest.slice(i, i + BATCH_SIZE)
            console.log(`[loadAllVerbs] Loading batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(manifest.length / BATCH_SIZE)}`)

            const batchPromises = batch.map(filename =>
                storage.getItem<Verb>(`appdata/api/verbs/${filename}`)
                    .catch((err) => {
                        console.error(`[loadAllVerbs] Failed to load ${filename}:`, err)
                        return null
                    })
            )

            const batchResults = await Promise.all(batchPromises)

            for (const verb of batchResults) {
                if (verb) {
                    verbs.push(verb)
                    // Build cross-refs while loading
                    if (verb.cross_reference) {
                        crossRefs[verb.root] = verb.cross_reference
                    }
                }
            }
        }

        if (verbs.length > 0) {
            console.log(`[loadAllVerbs] Loaded ${verbs.length} verbs successfully`)
            verbsCache = verbs
            verbsCacheTime = now
            return verbs
        }

        throw new Error('No verbs loaded')
    }
    catch (err) {
        console.error('[loadAllVerbs] Failed to load verbs:', err)
        throw createError({
            statusCode: 500,
            statusMessage: 'Failed to load verb data',
            data: { error: err }
        })
    }
}

/**
 * Load search index (lightweight, single file)
 * This is MUCH faster than loadAllVerbs for search operations
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
 * Clear the verbs cache (useful for development)
 */
export function clearVerbsCache() {
    verbsCache = null
    verbsCacheTime = 0
    searchIndexCache = null
}
