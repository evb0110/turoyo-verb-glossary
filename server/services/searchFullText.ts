import type { IExcerpt } from '~/types/IExcerpt'
import type { IVerb } from '~/types/IVerb'
import type { IVerbMetadata } from '~/types/IVerbMetadata'
import { extractMetadata } from '~~/server/services/extractMetadata'
import type { IFullTextSearchResult } from '~~/server/services/IFullTextSearchResult'
import type { ISearchOptions } from '~~/server/services/ISearchOptions'
import { matchesPattern } from '~~/server/utils/matchesPattern'
import { generateExcerpts } from '~~/server/utils/verbExcerpts'

export async function searchFullText(
    verbFiles: string[],
    query: string,
    opts: ISearchOptions & { searchType: 'roots' | 'all' }
): Promise<IFullTextSearchResult> {
    const storage = useStorage('assets:server')
    const matchingRoots: string[] = []
    const verbPreviews: Record<string, { verb?: IVerb
        excerpts?: IExcerpt[] }> = {}
    const verbMetadata: Record<string, IVerbMetadata> = {}

    const BATCH_SIZE = 100
    for (let i = 0; i < verbFiles.length; i += BATCH_SIZE) {
        const batch = verbFiles.slice(i, i + BATCH_SIZE)

        const batchPromises = batch.map(async (filePath: string) => {
            try {
                const verb = await storage.getItem<IVerb>(filePath)
                if (!verb) return null

                const root = verb.root

                if (matchesPattern(verb.root, query, opts)) {
                    if (opts.searchType === 'roots') {
                        verbPreviews[root] = {
                            verb,
                        }
                    }
                    else {
                        verbPreviews[root] = {
                            excerpts: generateExcerpts(verb, query, opts),
                        }
                    }
                    verbMetadata[root] = extractMetadata(verb)
                    return root
                }

                if (verb.lemma_header_tokens) {
                    for (const token of verb.lemma_header_tokens) {
                        if (matchesPattern(token.text, query, opts)) {
                            if (opts.searchType === 'roots') {
                                verbPreviews[root] = {
                                    verb,
                                }
                            }
                            else {
                                verbPreviews[root] = {
                                    excerpts: generateExcerpts(verb, query, opts),
                                }
                            }
                            verbMetadata[root] = extractMetadata(verb)
                            return root
                        }
                    }
                }

                for (const stem of verb.stems) {
                    if (stem.forms?.some(f => matchesPattern(f, query, opts))) {
                        if (opts.searchType === 'roots') {
                            verbPreviews[root] = {
                                verb,
                            }
                        }
                        else {
                            verbPreviews[root] = {
                                excerpts: generateExcerpts(verb, query, opts),
                            }
                        }
                        verbMetadata[root] = extractMetadata(verb)
                        return root
                    }

                    if (stem.label_gloss_tokens) {
                        for (const token of stem.label_gloss_tokens) {
                            if (matchesPattern(token.text, query, opts)) {
                                if (opts.searchType === 'roots') {
                                    verbPreviews[root] = {
                                        verb,
                                    }
                                }
                                else {
                                    verbPreviews[root] = {
                                        excerpts: generateExcerpts(verb, query, opts),
                                    }
                                }
                                verbMetadata[root] = extractMetadata(verb)
                                return root
                            }
                        }
                    }

                    for (const examples of Object.values(stem.conjugations)) {
                        for (const example of examples) {
                            for (const translation of example.translations) {
                                if (matchesPattern(translation, query, opts)) {
                                    if (opts.searchType === 'roots') {
                                        verbPreviews[root] = {
                                            verb,
                                        }
                                    }
                                    else {
                                        verbPreviews[root] = {
                                            excerpts: generateExcerpts(verb, query, opts),
                                        }
                                    }
                                    verbMetadata[root] = extractMetadata(verb)
                                    return root
                                }
                            }

                            if (matchesPattern(example.turoyo, query, opts)) {
                                if (opts.searchType === 'roots') {
                                    verbPreviews[root] = {
                                        verb,
                                    }
                                }
                                else {
                                    verbPreviews[root] = {
                                        excerpts: generateExcerpts(verb, query, opts),
                                    }
                                }
                                verbMetadata[root] = extractMetadata(verb)
                                return root
                            }

                            for (const reference of example.references) {
                                if (matchesPattern(reference, query, opts)) {
                                    if (opts.searchType === 'roots') {
                                        verbPreviews[root] = {
                                            verb,
                                        }
                                    }
                                    else {
                                        verbPreviews[root] = {
                                            excerpts: generateExcerpts(verb, query, opts),
                                        }
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
                            (etymon.meaning && matchesPattern(etymon.meaning, query, opts))
                            || (etymon.notes && matchesPattern(etymon.notes, query, opts))
                            || (etymon.raw && matchesPattern(etymon.raw, query, opts))
                            || (etymon.source_root && matchesPattern(etymon.source_root, query, opts))
                        ) {
                            if (opts.searchType === 'roots') {
                                verbPreviews[root] = {
                                    verb,
                                }
                            }
                            else {
                                verbPreviews[root] = {
                                    excerpts: generateExcerpts(verb, query, opts),
                                }
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
        verbMetadata,
    }
}
