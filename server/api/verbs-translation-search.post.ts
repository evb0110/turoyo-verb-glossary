import { matchesPattern } from '../utils/regexSearch'
import type { Verb } from '../utils/verbs'
import { generateExcerpts, type Excerpt } from '../utils/verbExcerpts'
import { generateFullPreview } from '../utils/verbHtmlPreview'

/**
 * Server-side translation search endpoint
 * Loads verb files and searches through translations/glosses
 * POST to avoid URL length limits and send roots array
 *
 * Returns pre-rendered HTML for both "roots only" and "everything" modes
 */
export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const { roots, query, useRegex, caseSensitive, searchType } = body

    if (!roots || !Array.isArray(roots) || !query) {
        throw createError({
            statusCode: 400,
            message: 'Invalid request: roots array and query required'
        })
    }

    console.log(`[Translation Search] Searching ${roots.length} verbs for: "${query}" (mode: ${searchType})`)

    const matchingRoots: string[] = []
    const verbPreviews: Record<string, { excerpts?: Excerpt[], preview?: string }> = {} // Pre-rendered HTML

    // Use Nitro's server assets storage (works in both dev and production)
    // Files from server/assets/ are bundled with server code
    const storage = useStorage('assets:server')

    // Process in batches to avoid memory issues
    const BATCH_SIZE = 50
    for (let i = 0; i < roots.length; i += BATCH_SIZE) {
        const batch = roots.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (root: string) => {
            try {
                // Load verb file from server assets (bundled with server code)
                const verb = await storage.getItem<Verb>(`appdata/api/verbs/${root}.json`)

                if (!verb) {
                    console.warn(`[Translation Search] No data for ${root}`)
                    return null
                }

                // Search in root
                if (matchesPattern(verb.root, query, { useRegex, caseSensitive })) {
                    // Generate appropriate preview based on search type
                    if (searchType === 'roots') {
                        verbPreviews[root] = { preview: generateFullPreview(verb) }
                    }
                    else {
                        verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                    }
                    return root
                }

                // Search in lemma header (contains bibliographic references, citations, attributions)
                if (verb.lemma_header_tokens) {
                    for (const token of verb.lemma_header_tokens) {
                        if (matchesPattern(token.text, query, { useRegex, caseSensitive })) {
                            if (searchType === 'roots') {
                                verbPreviews[root] = { preview: generateFullPreview(verb) }
                            }
                            else {
                                verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                            }
                            return root
                        }
                    }
                }

                // Search in forms
                for (const stem of verb.stems) {
                    if (stem.forms?.some(f => matchesPattern(f, query, { useRegex, caseSensitive }))) {
                        if (searchType === 'roots') {
                            verbPreviews[root] = { preview: generateFullPreview(verb) }
                        }
                        else {
                            verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                        }
                        return root
                    }

                    // Search in glosses
                    if (stem.label_gloss_tokens) {
                        for (const token of stem.label_gloss_tokens) {
                            if (matchesPattern(token.text, query, { useRegex, caseSensitive })) {
                                if (searchType === 'roots') {
                                    verbPreviews[root] = { preview: generateFullPreview(verb) }
                                }
                                else {
                                    verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                }
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
                            return root
                        }
                    }
                }

                return null
            }
            catch (e) {
                console.warn(`[Translation Search] Failed to load ${root}:`, e)
                return null
            }
        })

        const batchResults = await Promise.all(batchPromises)
        matchingRoots.push(...batchResults.filter((r): r is string => r !== null))
    }

    console.log(`[Translation Search] Found ${matchingRoots.length} matches`)

    // Return both roots and pre-rendered HTML previews (SSR)
    return {
        total: matchingRoots.length,
        roots: matchingRoots,
        verbPreviews // Pre-rendered HTML (either excerpts or full previews)
    }
})
