import { matchesPattern } from '../utils/regexSearch'
import type { Verb, Excerpt, VerbMetadata } from '~/types/verb'
import { generateExcerpts } from '../utils/verbExcerpts'

function extractMetadata(verb: Verb): VerbMetadata {
    const etymologySources: string[] = []

    if (verb.etymology?.etymons) {
        for (const etymon of verb.etymology.etymons) {
            if (etymon.source) {
                if (!etymologySources.includes(etymon.source)) {
                    etymologySources.push(etymon.source)
                }
            }

            else if (etymon.raw) {
                const langMatch = etymon.raw.match(/(?:cf\.\s*)?<\s*([A-Z][a-z]*\.?)/)
                if (langMatch && langMatch[1]) {
                    const lang = langMatch[1]
                    if (!etymologySources.includes(lang)) {
                        etymologySources.push(lang)
                    }
                }
                else if (!etymologySources.includes('Unknown')) {
                    etymologySources.push('Unknown')
                }
            }
        }
    }

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
    const verbPreviews: Record<string, { excerpts?: Excerpt[], verb?: Verb }> = {}
    const verbMetadata: Record<string, VerbMetadata> = {}

    const allFiles = await storage.getKeys('verbs')
    const verbFiles = allFiles.filter(f => f.endsWith('.json'))

    console.log(`[Verb Search] Total verb files: ${verbFiles.length}`)
    if (verbFiles.length > 0) {
        console.log(`[Verb Search] First 3 file paths:`, verbFiles.slice(0, 3))
    }

    const allRoots = verbFiles.map((f) => {
        const filename = f.split(':').pop() || f

        const root = filename.replace(/\.json$/, '')
        return root
    })

    if (allRoots.length > 0) {
        console.log(`[Verb Search] First 3 extracted roots:`, allRoots.slice(0, 3))
    }

    if (searchType === 'roots') {
        console.log('[Verb Search] Roots-only mode: searching filenames...')

        const filteredRoots = allRoots.filter(root =>
            matchesPattern(root, query, { useRegex, caseSensitive })
        )

        console.log(`[Verb Search] Found ${filteredRoots.length} matching roots`)

        const BATCH_SIZE = 50
        for (let i = 0; i < filteredRoots.length; i += BATCH_SIZE) {
            const batch = filteredRoots.slice(i, i + BATCH_SIZE)

            const batchPromises = batch.map(async (root: string) => {
                try {
                    const verb = await storage.getItem<Verb>(`verbs/${root}.json`)
                    if (!verb) return null

                    verbPreviews[root] = { verb }

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

    console.log('[Verb Search] Everything mode: scanning all verb content...')

    const BATCH_SIZE = 100
    for (let i = 0; i < verbFiles.length; i += BATCH_SIZE) {
        const batch = verbFiles.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (filePath: string) => {
            try {
                const verb = await storage.getItem<Verb>(filePath)
                if (!verb) return null

                const root = verb.root

                if (matchesPattern(verb.root, query, { useRegex, caseSensitive })) {
                    if (searchType === 'roots') {
                        verbPreviews[root] = { verb }
                    }
                    else {
                        verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                    }
                    verbMetadata[root] = extractMetadata(verb)
                    return root
                }

                if (verb.lemma_header_tokens) {
                    for (const token of verb.lemma_header_tokens) {
                        if (matchesPattern(token.text, query, { useRegex, caseSensitive })) {
                            if (searchType === 'roots') {
                                verbPreviews[root] = { verb }
                            }
                            else {
                                verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                            }
                            verbMetadata[root] = extractMetadata(verb)
                            return root
                        }
                    }
                }

                for (const stem of verb.stems) {
                    if (stem.forms?.some(f => matchesPattern(f, query, { useRegex, caseSensitive }))) {
                        if (searchType === 'roots') {
                            verbPreviews[root] = { verb }
                        }
                        else {
                            verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                        }
                        verbMetadata[root] = extractMetadata(verb)
                        return root
                    }

                    if (stem.label_gloss_tokens) {
                        for (const token of stem.label_gloss_tokens) {
                            if (matchesPattern(token.text, query, { useRegex, caseSensitive })) {
                                if (searchType === 'roots') {
                                    verbPreviews[root] = { verb }
                                }
                                else {
                                    verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                }
                                verbMetadata[root] = extractMetadata(verb)
                                return root
                            }
                        }
                    }

                    for (const examples of Object.values(stem.conjugations)) {
                        for (const example of examples) {
                            for (const translation of example.translations) {
                                if (matchesPattern(translation, query, { useRegex, caseSensitive })) {
                                    if (searchType === 'roots') {
                                        verbPreviews[root] = { verb }
                                    }
                                    else {
                                        verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                    }
                                    verbMetadata[root] = extractMetadata(verb)
                                    return root
                                }
                            }

                            if (matchesPattern(example.turoyo, query, { useRegex, caseSensitive })) {
                                if (searchType === 'roots') {
                                    verbPreviews[root] = { verb }
                                }
                                else {
                                    verbPreviews[root] = { excerpts: generateExcerpts(verb, query, { useRegex, caseSensitive }) }
                                }
                                verbMetadata[root] = extractMetadata(verb)
                                return root
                            }

                            for (const reference of example.references) {
                                if (matchesPattern(reference, query, { useRegex, caseSensitive })) {
                                    if (searchType === 'roots') {
                                        verbPreviews[root] = { verb }
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

                if (verb.etymology && Array.isArray(verb.etymology.etymons)) {
                    for (const etymon of verb.etymology.etymons) {
                        if (
                            (etymon.meaning && matchesPattern(etymon.meaning, query, { useRegex, caseSensitive }))
                            || (etymon.notes && matchesPattern(etymon.notes, query, { useRegex, caseSensitive }))
                            || (etymon.raw && matchesPattern(etymon.raw, query, { useRegex, caseSensitive }))
                            || (etymon.source_root && matchesPattern(etymon.source_root, query, { useRegex, caseSensitive }))
                        ) {
                            if (searchType === 'roots') {
                                verbPreviews[root] = { verb }
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

    return {
        total: matchingRoots.length,
        roots: matchingRoots,
        verbPreviews,
        verbMetadata
    }
})
