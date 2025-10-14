import { matchesPattern } from '../utils/regexSearch'
import type { Verb } from '../utils/verbs'
import { generateExcerpts, type Excerpt } from '../utils/verbExcerpts'
import { generateFullPreview } from '../utils/verbHtmlPreview'

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

    const storage = useStorage('assets:server')

    const BATCH_SIZE = 50
    for (let i = 0; i < roots.length; i += BATCH_SIZE) {
        const batch = roots.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (root: string) => {
            try {
                const verb = await storage.getItem<Verb>(`appdata/api/verbs/${root}.json`)

                if (!verb) {
                    console.warn(`[Translation Search] No data for ${root}`)
                    return null
                }

                if (matchesPattern(verb.root, query, { useRegex, caseSensitive })) {
                    if (searchType === 'roots') {
                        verbPreviews[root] = { preview: generateFullPreview(verb) }
                    }
                    else {
                        verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                    }
                    return root
                }

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

                    for (const examples of Object.values(stem.conjugations)) {
                        for (const example of examples) {
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

                            if (matchesPattern(example.turoyo, query, { useRegex, caseSensitive })) {
                                if (searchType === 'roots') {
                                    verbPreviews[root] = { preview: generateFullPreview(verb) }
                                }
                                else {
                                    verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                }
                                return root
                            }

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

    return {
        total: matchingRoots.length,
        roots: matchingRoots,
        verbPreviews // Pre-rendered HTML (either excerpts or full previews)
    }
})
