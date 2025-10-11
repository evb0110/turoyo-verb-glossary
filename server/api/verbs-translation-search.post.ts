import { matchesPattern } from '../utils/regexSearch'
import type { Verb } from '../utils/verbs'

/**
 * Server-side translation search endpoint
 * Loads verb files and searches through translations/glosses
 * POST to avoid URL length limits and send roots array
 */
export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const { roots, query, useRegex, caseSensitive } = body

    if (!roots || !Array.isArray(roots) || !query) {
        throw createError({
            statusCode: 400,
            message: 'Invalid request: roots array and query required'
        })
    }

    console.log(`[Translation Search] Searching ${roots.length} verbs for: "${query}"`)

    const matchingRoots: string[] = []
    const verbData: Record<string, Verb> = {} // Cache loaded verbs to return

    // Process in batches to avoid memory issues
    const BATCH_SIZE = 50
    for (let i = 0; i < roots.length; i += BATCH_SIZE) {
        const batch = roots.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (root: string) => {
            try {
                const encodedRoot = encodeURIComponent(root)
                // Use $fetch with base URL for server-side fetch
                const baseURL = process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3456'
                const verb = await $fetch<Verb>(`/appdata/api/verbs/${encodedRoot}.json`, { baseURL })

                if (!verb) {
                    console.warn(`[Translation Search] No data for ${root}`)
                    return null
                }

                // Search in root
                if (matchesPattern(verb.root, query, { useRegex, caseSensitive })) {
                    verbData[root] = verb // Cache the loaded verb
                    return root
                }

                // Search in forms
                for (const stem of verb.stems) {
                    if (stem.forms?.some(f => matchesPattern(f, query, { useRegex, caseSensitive }))) {
                        verbData[root] = verb
                        return root
                    }

                    // Search in glosses
                    if (stem.label_gloss_tokens) {
                        for (const token of stem.label_gloss_tokens) {
                            if (matchesPattern(token.text, query, { useRegex, caseSensitive })) {
                                verbData[root] = verb
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
                                    verbData[root] = verb
                                    return root
                                }
                            }

                            // Search in Turoyo text
                            if (matchesPattern(example.turoyo, query, { useRegex, caseSensitive })) {
                                verbData[root] = verb
                                return root
                            }

                            // Search in references/citations
                            for (const reference of example.references) {
                                if (matchesPattern(reference, query, { useRegex, caseSensitive })) {
                                    verbData[root] = verb
                                    return root
                                }
                            }
                        }
                    }
                }

                // Search in etymology
                if (verb.etymology) {
                    for (const etymon of verb.etymology.etymons) {
                        if (etymon.meaning && matchesPattern(etymon.meaning, query, { useRegex, caseSensitive })) {
                            verbData[root] = verb
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

    // Return both roots and cached verb data to avoid duplicate client-side loading
    return {
        total: matchingRoots.length,
        roots: matchingRoots,
        verbData // Include full verb data for previews (already loaded during search)
    }
})
