import { matchesPattern } from '../utils/regexSearch'
import type { Verb } from '../utils/verbs'
import { generateExcerpts, type Excerpt } from '../utils/verbExcerpts'
import { generateFullPreview } from '../utils/verbHtmlPreview'

/**
 * Unified verb search endpoint
 *
 * "Roots only" mode: Searches filenames (super fast - no file reads!)
 * "Everything" mode: Searches all fields in all verb files
 *
 * Returns matching roots and pre-rendered HTML previews (SSR-ready)
 */
interface VerbMetadata {
    root: string
    etymology_sources: string[]
    stems: string[]
}

/**
 * Extract metadata from a verb for filtering
 */
function extractMetadata(verb: Verb): VerbMetadata {
    const etymologySources = verb.etymology?.etymons
        ? verb.etymology.etymons.map(e => e.source).filter(Boolean)
        : []

    const stems = verb.stems
        .map(s => s.stem)
        .filter((s): s is string => Boolean(s))

    return {
        root: verb.root,
        etymology_sources: etymologySources,
        stems
    }
}

export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const { query, useRegex, caseSensitive, searchType } = body

    if (!query) {
        throw createError({
            statusCode: 400,
            message: 'Invalid request: query required'
        })
    }

    console.log(`[Verb Search] Query: "${query}", Mode: ${searchType}, Regex: ${useRegex}, Case: ${caseSensitive}`)

    const storage = useStorage('assets:server')
    const matchingRoots: string[] = []
    const verbPreviews: Record<string, { excerpts?: Excerpt[], preview?: string }> = {}
    const verbMetadata: Record<string, VerbMetadata> = {}

    // Get all verb filenames (the filenames ARE the roots!)
    // Note: storage.getKeys() returns keys relative to the base path
    const allFiles = await storage.getKeys('appdata/api/verbs')
    const verbFiles = allFiles.filter(f => f.endsWith('.json'))

    console.log(`[Verb Search] Total verb files: ${verbFiles.length}`)
    if (verbFiles.length > 0) {
        console.log(`[Verb Search] First 3 file paths:`, verbFiles.slice(0, 3))
    }

    // Extract roots from filenames
    // Storage keys use colons as delimiters: "appdata:api:verbs:kfr.json"
    const allRoots = verbFiles.map((f) => {
        // Get the filename only (everything after last colon)
        const filename = f.split(':').pop() || f
        // Remove .json extension
        const root = filename.replace(/\.json$/, '')
        return root
    })

    if (allRoots.length > 0) {
        console.log(`[Verb Search] First 3 extracted roots:`, allRoots.slice(0, 3))
    }

    // MODE 1: "Roots only" - Search filenames only (super fast!)
    if (searchType === 'roots') {
        console.log('[Verb Search] Roots-only mode: searching filenames...')

        // Filter roots by query
        const filteredRoots = allRoots.filter(root =>
            matchesPattern(root, query, { useRegex, caseSensitive })
        )

        console.log(`[Verb Search] Found ${filteredRoots.length} matching roots`)

        // Load matched verb files to generate previews
        const BATCH_SIZE = 50
        for (let i = 0; i < filteredRoots.length; i += BATCH_SIZE) {
            const batch = filteredRoots.slice(i, i + BATCH_SIZE)

            const batchPromises = batch.map(async (root: string) => {
                try {
                    const verb = await storage.getItem<Verb>(`appdata/api/verbs/${root}.json`)
                    if (!verb) return null

                    // Generate full article preview for roots-only mode
                    verbPreviews[root] = { preview: generateFullPreview(verb) }

                    // Extract metadata for filtering
                    verbMetadata[root] = extractMetadata(verb)

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
            verbPreviews,
            verbMetadata
        }
    }

    // MODE 2: "Everything" - Search all fields in all files
    console.log('[Verb Search] Everything mode: scanning all verb content...')

    // Process in batches to avoid memory issues
    const BATCH_SIZE = 100
    for (let i = 0; i < verbFiles.length; i += BATCH_SIZE) {
        const batch = verbFiles.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (filePath: string) => {
            try {
                const verb = await storage.getItem<Verb>(filePath)
                if (!verb) return null

                const root = verb.root

                // Search in root
                if (matchesPattern(verb.root, query, { useRegex, caseSensitive })) {
                    if (searchType === 'roots') {
                        verbPreviews[root] = { preview: generateFullPreview(verb) }
                    }
                    else {
                        verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                    }
                    verbMetadata[root] = extractMetadata(verb)
                    return root
                }

                // Search in lemma header (bibliographic references, citations, attributions)
                if (verb.lemma_header_tokens) {
                    for (const token of verb.lemma_header_tokens) {
                        if (matchesPattern(token.text, query, { useRegex, caseSensitive })) {
                            if (searchType === 'roots') {
                                verbPreviews[root] = { preview: generateFullPreview(verb) }
                            }
                            else {
                                verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                            }
                            verbMetadata[root] = extractMetadata(verb)
                            return root
                        }
                    }
                }

                // Search in forms and glosses
                for (const stem of verb.stems) {
                    // Search in forms
                    if (stem.forms?.some(f => matchesPattern(f, query, { useRegex, caseSensitive }))) {
                        if (searchType === 'roots') {
                            verbPreviews[root] = { preview: generateFullPreview(verb) }
                        }
                        else {
                            verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                        }
                        verbMetadata[root] = extractMetadata(verb)
                        return root
                    }

                    // Search in glosses (meanings)
                    if (stem.label_gloss_tokens) {
                        for (const token of stem.label_gloss_tokens) {
                            if (matchesPattern(token.text, query, { useRegex, caseSensitive })) {
                                if (searchType === 'roots') {
                                    verbPreviews[root] = { preview: generateFullPreview(verb) }
                                }
                                else {
                                    verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                }
                                verbMetadata[root] = extractMetadata(verb)
                                return root
                            }
                        }
                    }

                    // Search in examples (translations, turoyo text, and references)
                    for (const examples of Object.values(stem.conjugations)) {
                        for (const example of examples) {
                            // Search in English translations
                            for (const translation of example.translations) {
                                if (matchesPattern(translation, query, { useRegex, caseSensitive })) {
                                    if (searchType === 'roots') {
                                        verbPreviews[root] = { preview: generateFullPreview(verb) }
                                    }
                                    else {
                                        verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                    }
                                    verbMetadata[root] = extractMetadata(verb)
                                    return root
                                }
                            }

                            // Search in Turoyo text
                            if (matchesPattern(example.turoyo, query, { useRegex, caseSensitive })) {
                                if (searchType === 'roots') {
                                    verbPreviews[root] = { preview: generateFullPreview(verb) }
                                }
                                else {
                                    verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                }
                                verbMetadata[root] = extractMetadata(verb)
                                return root
                            }

                            // Search in references/citations
                            for (const reference of example.references) {
                                if (matchesPattern(reference, query, { useRegex, caseSensitive })) {
                                    if (searchType === 'roots') {
                                        verbPreviews[root] = { preview: generateFullPreview(verb) }
                                    }
                                    else {
                                        verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                    }
                                    verbMetadata[root] = extractMetadata(verb)
                                    return root
                                }
                            }
                        }
                    }
                }

                // Search in etymology (all fields: meaning, notes, raw, source_root)
                if (verb.etymology && Array.isArray(verb.etymology.etymons)) {
                    for (const etymon of verb.etymology.etymons) {
                        if (
                            (etymon.meaning && matchesPattern(etymon.meaning, query, { useRegex, caseSensitive }))
                            || (etymon.notes && matchesPattern(etymon.notes, query, { useRegex, caseSensitive }))
                            || (etymon.raw && matchesPattern(etymon.raw, query, { useRegex, caseSensitive }))
                            || (etymon.source_root && matchesPattern(etymon.source_root, query, { useRegex, caseSensitive }))
                        ) {
                            if (searchType === 'roots') {
                                verbPreviews[root] = { preview: generateFullPreview(verb) }
                            }
                            else {
                                verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                            }
                            verbMetadata[root] = extractMetadata(verb)
                            return root
                        }
                    }
                }

                return null
            }
            catch (e) {
                console.warn(`[Full-text Search] Failed to load ${filePath}:`, e)
                return null
            }
        })

        const batchResults = await Promise.all(batchPromises)
        matchingRoots.push(...batchResults.filter((r): r is string => r !== null))
    }

    console.log(`[Full-text Search] Found ${matchingRoots.length} matches`)

    // Return matching roots, pre-rendered HTML previews, and metadata for filters
    return {
        total: matchingRoots.length,
        roots: matchingRoots,
        verbPreviews, // Pre-rendered HTML (either excerpts or full previews)
        verbMetadata // Metadata for generating filter options
    }
})
