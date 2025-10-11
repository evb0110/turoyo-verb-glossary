/**
 * Server-side utilities for generating contextual excerpts from verb data
 * Used for "everything" search mode to show matches in context
 */

import type { Verb } from './verbs'
import { createSearchRegex, matchAll } from './regexSearch'
import { extractContext, tokenTextToString } from './textUtils'
import { highlightMatches } from './highlightSSR'

export interface Excerpt {
    type: 'form' | 'example' | 'translation' | 'etymology' | 'gloss'
    stem?: string
    conjugationType?: string
    text: string
    html: string // HTML version with highlights
    label: string
}

/**
 * Helper to add an excerpt if it's unique
 * Reduces duplication of excerpt creation pattern
 */
function addExcerpt(
    excerpts: Excerpt[],
    seenTexts: Set<string>,
    excerptText: string,
    excerpt: Omit<Excerpt, 'text'>
): void {
    if (!seenTexts.has(excerptText)) {
        seenTexts.add(excerptText)
        excerpts.push({
            ...excerpt,
            text: excerptText
        })
    }
}

/**
 * Generate contextual excerpts showing matches in verb content
 * Used for "everything" search mode
 *
 * @param verb - The verb to search within
 * @param query - Search query string
 * @param opts - Search options
 * @returns Array of excerpts with highlighted matches
 *
 * @example
 * const excerpts = generateExcerpts(verb, 'learn', {
 *   useRegex: false,
 *   caseSensitive: false,
 *   maxExcerpts: 5
 * })
 */
export function generateExcerpts(
    verb: Verb,
    query: string,
    opts: {
        useRegex?: boolean
        caseSensitive?: boolean
        maxExcerpts?: number
    } = {}
): Excerpt[] {
    const excerpts: Excerpt[] = []
    const regex = createSearchRegex(query, opts)
    if (!regex) {
        return excerpts // Invalid regex, return empty
    }

    const maxExcerpts = opts.maxExcerpts ?? 5
    const seenTexts = new Set<string>() // Track unique texts to avoid duplicates

    // 1. Search in lemma header (bibliographic references, citations, attributions)
    if (verb.lemma_header_tokens) {
        const headerText = tokenTextToString(verb.lemma_header_tokens)

        // Find ALL matches using the matchAll generator
        for (const match of matchAll(headerText, regex)) {
            if (excerpts.length >= maxExcerpts) break

            const excerptText = extractContext(headerText, match.index, match[0].length, 60)
            addExcerpt(excerpts, seenTexts, excerptText, {
                type: 'etymology', // Using 'etymology' type for header citations
                html: highlightMatches(excerptText, query, opts),
                label: 'Citation:'
            })
        }
    }

    // 2. Search in forms
    for (const stem of verb.stems) {
        for (const form of stem.forms) {
            if (regex.test(form)) {
                addExcerpt(excerpts, seenTexts, form, {
                    type: 'form',
                    stem: stem.stem,
                    html: highlightMatches(form, query, opts),
                    label: `Form (Stem ${stem.stem})`
                })
            }
        }

        // 3. Search in stem glosses (German meanings)
        if (stem.label_gloss_tokens) {
            const glossText = tokenTextToString(stem.label_gloss_tokens)

            // Find ALL matches using the matchAll generator
            for (const match of matchAll(glossText, regex)) {
                if (excerpts.length >= maxExcerpts) break

                const excerptText = extractContext(glossText, match.index, match[0].length, 60)
                addExcerpt(excerpts, seenTexts, excerptText, {
                    type: 'gloss',
                    stem: stem.stem,
                    html: highlightMatches(excerptText, query, opts),
                    label: `Meaning (Stem ${stem.stem}):`
                })
            }
        }

        // 4. Search in conjugation examples
        for (const [conjType, examples] of Object.entries(stem.conjugations)) {
            for (const example of examples) {
                // Skip if we have enough excerpts
                if (excerpts.length >= maxExcerpts) {
                    return excerpts
                }

                // Search in turoyo text
                if (example.turoyo) {
                    const tMatch = example.turoyo.match(regex)
                    if (tMatch && tMatch.index !== undefined) {
                        const excerptText = extractContext(example.turoyo, tMatch.index, tMatch[0].length, 60)
                        addExcerpt(excerpts, seenTexts, excerptText, {
                            type: 'example',
                            stem: stem.stem,
                            conjugationType: conjType,
                            html: highlightMatches(excerptText, query, opts),
                            label: `${conjType}:`
                        })
                    }
                }

                // Search in translations
                for (const translation of example.translations) {
                    if (excerpts.length >= maxExcerpts) {
                        return excerpts
                    }

                    if (translation) {
                        const trMatch = translation.match(regex)
                        if (trMatch && trMatch.index !== undefined) {
                            const excerptText = extractContext(translation, trMatch.index, trMatch[0].length, 60)
                            addExcerpt(excerpts, seenTexts, excerptText, {
                                type: 'translation',
                                stem: stem.stem,
                                conjugationType: conjType,
                                html: highlightMatches(excerptText, query, opts),
                                label: `Translation:`
                            })
                        }
                    }
                }
            }
        }
    }

    // 5. Search in etymology (all fields: meaning, notes, raw, source_root)
    if (verb.etymology && Array.isArray(verb.etymology.etymons)) {
        for (const etymon of verb.etymology.etymons) {
            if (excerpts.length >= maxExcerpts) {
                break
            }

            // Search in all text fields of the etymon
            const searchFields = [
                etymon.meaning,
                etymon.notes,
                etymon.raw,
                etymon.source_root
            ].filter((field): field is string => Boolean(field)) // Type-safe filter

            for (const field of searchFields) {
                // Find ALL matches using the matchAll generator
                for (const match of matchAll(field, regex)) {
                    if (excerpts.length >= maxExcerpts) break

                    const excerptText = extractContext(field, match.index, match[0].length, 60)
                    addExcerpt(excerpts, seenTexts, excerptText, {
                        type: 'etymology',
                        html: highlightMatches(excerptText, query, opts),
                        label: `Etymology:`
                    })
                }
            }
        }
    }

    return excerpts.slice(0, maxExcerpts)
}
