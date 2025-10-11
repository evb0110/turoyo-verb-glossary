/**
 * Utilities for generating verb article previews in search results
 */

import type { Verb, VerbIndexEntry } from '~/composables/useVerbs'
import { createSearchRegex } from '~/utils/regexSearch'

export interface Excerpt {
    type: 'form' | 'example' | 'translation' | 'etymology' | 'gloss'
    stem?: string
    conjugationType?: string
    text: string
    label: string
}

/**
 * Batch load full verb data for search results
 * Loads all verbs in parallel for best performance
 */
export async function loadVerbsForResults(
    results: VerbIndexEntry[]
): Promise<Map<string, Verb>> {
    const { getVerb } = useVerbs()
    const verbMap = new Map<string, Verb>()

    console.log(`[verbPreview] Loading ${results.length} verbs...`)

    // Load all in parallel
    await Promise.all(
        results.map(async (entry) => {
            try {
                const verb = await getVerb(entry.root)
                verbMap.set(entry.root, verb)
            }
            catch (e) {
                console.warn(`[verbPreview] Failed to load verb ${entry.root}:`, e)
            }
        })
    )

    console.log(`[verbPreview] Loaded ${verbMap.size} verbs successfully`)
    return verbMap
}

/**
 * Generate contextual excerpts showing matches in verb content
 * Used for "everything" search mode
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
    const maxExcerpts = opts.maxExcerpts ?? 5
    const seenTexts = new Set<string>() // Track unique texts to avoid duplicates

    // 1. Search in forms
    for (const stem of verb.stems) {
        for (const form of stem.forms) {
            if (regex.test(form) && !seenTexts.has(form)) {
                seenTexts.add(form)
                excerpts.push({
                    type: 'form',
                    stem: stem.stem,
                    text: form,
                    label: `Form (Stem ${stem.stem})`
                })
            }
        }

        // 2. Search in stem glosses (German meanings)
        if (stem.label_gloss_tokens) {
            const glossText = stem.label_gloss_tokens
                .map(token => token.text)
                .join('')

            const glossMatch = glossText.match(regex)
            if (glossMatch && glossMatch.index !== undefined) {
                const excerptText = extractContext(glossText, glossMatch.index, glossMatch[0].length, 60)
                if (!seenTexts.has(excerptText)) {
                    seenTexts.add(excerptText)
                    excerpts.push({
                        type: 'gloss',
                        stem: stem.stem,
                        text: excerptText,
                        label: `Meaning (Stem ${stem.stem}):`
                    })
                }
            }
        }

        // 3. Search in conjugation examples
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
                        if (!seenTexts.has(excerptText)) {
                            seenTexts.add(excerptText)
                            excerpts.push({
                                type: 'example',
                                stem: stem.stem,
                                conjugationType: conjType,
                                text: excerptText,
                                label: `${conjType}:`
                            })
                        }
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
                            if (!seenTexts.has(excerptText)) {
                                seenTexts.add(excerptText)
                                excerpts.push({
                                    type: 'translation',
                                    stem: stem.stem,
                                    conjugationType: conjType,
                                    text: excerptText,
                                    label: `Translation:`
                                })
                            }
                        }
                    }
                }
            }
        }
    }

    // 4. Search in etymology
    if (verb.etymology) {
        for (const etymon of verb.etymology.etymons) {
            if (excerpts.length >= maxExcerpts) {
                break
            }

            if (etymon.meaning) {
                const eMatch = etymon.meaning.match(regex)
                if (eMatch && eMatch.index !== undefined) {
                    const excerptText = extractContext(etymon.meaning, eMatch.index, eMatch[0].length, 60)
                    if (!seenTexts.has(excerptText)) {
                        seenTexts.add(excerptText)
                        excerpts.push({
                            type: 'etymology',
                            text: excerptText,
                            label: `Etymology:`
                        })
                    }
                }
            }
        }
    }

    return excerpts.slice(0, maxExcerpts)
}

/**
 * Extract text context around a match position
 * Adds ellipsis if text is truncated
 */
function extractContext(
    text: string,
    matchPos: number,
    matchLength: number,
    contextLength: number
): string {
    const start = Math.max(0, matchPos - contextLength)
    const end = Math.min(text.length, matchPos + matchLength + contextLength)

    let result = text.slice(start, end)

    // Add ellipsis if truncated
    if (start > 0) {
        result = '...' + result
    }
    if (end < text.length) {
        result = result + '...'
    }

    return result
}

/**
 * Generate full article preview for root search mode
 * Shows etymology, stems with forms, glosses, and sample examples
 */
export function generateFullPreview(
    verb: Verb,
    opts: {
        maxExamplesPerStem?: number
        maxExampleLength?: number
    } = {}
): string {
    const maxExamplesPerStem = opts.maxExamplesPerStem ?? 3
    const maxExampleLength = opts.maxExampleLength ?? 150

    const parts: string[] = []

    // Etymology section
    if (verb.etymology && verb.etymology.etymons.length > 0) {
        const etymonParts = verb.etymology.etymons.map((etymon) => {
            const sourcePart = etymon.source_root
                ? `${etymon.source} ${etymon.source_root}`
                : etymon.source
            const meaningPart = etymon.meaning ? ` — ${etymon.meaning}` : ''
            return `< ${sourcePart}${meaningPart}`
        })

        parts.push(
            `<div class="preview-etymology"><strong>Etymology:</strong> ${etymonParts.join('; ')}</div>`
        )
    }

    // Stems
    for (const stem of verb.stems) {
        const stemParts: string[] = []

        // Stem header with forms
        const formsText = stem.forms.length > 0 ? stem.forms.join(', ') : '(no forms)'
        stemParts.push(`<div class="preview-stem-header"><strong>Stem ${stem.stem}:</strong> <span class="turoyo-text">${formsText}</span></div>`)

        // Gloss (German meaning) if available
        if (stem.label_gloss_tokens && stem.label_gloss_tokens.length > 0) {
            const glossText = stem.label_gloss_tokens
                .filter(token => !token.text.match(/^(I{1,3}|IV|Pa\.|Af\.|Detransitive):/)) // Skip stem label
                .map(token => token.text.trim())
                .join('')
                .trim()

            if (glossText) {
                const truncatedGloss = glossText.length > 100
                    ? glossText.slice(0, 100) + '...'
                    : glossText
                stemParts.push(`<div class="preview-gloss">${truncatedGloss}</div>`)
            }
        }

        // Sample examples
        const examples = collectExamples(stem.conjugations, maxExamplesPerStem)

        if (examples.length > 0) {
            const exampleItems = examples.map((ex) => {
                const turoyo = truncateText(ex.turoyo, maxExampleLength)
                const translation = ex.translations.length > 0
                    ? truncateText(ex.translations[0], maxExampleLength)
                    : ''
                const refs = ex.references.length > 0
                    ? ` <span class="preview-ref">[${ex.references[0]}]</span>`
                    : ''

                return translation
                    ? `<li><span class="turoyo-text">${turoyo}</span> — ${translation}${refs}</li>`
                    : `<li><span class="turoyo-text">${turoyo}</span>${refs}</li>`
            })

            stemParts.push(`<ul class="preview-examples">${exampleItems.join('')}</ul>`)
        }

        parts.push(`<div class="preview-stem">${stemParts.join('')}</div>`)
    }

    return parts.join('')
}

/**
 * Collect examples from conjugations, up to a maximum count
 */
function collectExamples(
    conjugations: { [key: string]: Array<{ turoyo: string, translations: string[], references: string[] }> },
    maxCount: number
): Array<{ turoyo: string, translations: string[], references: string[] }> {
    const examples: Array<{ turoyo: string, translations: string[], references: string[] }> = []

    for (const [_conjType, exampleList] of Object.entries(conjugations)) {
        for (const example of exampleList) {
            if (examples.length >= maxCount) {
                return examples
            }

            // Skip empty examples
            if (example.turoyo && example.turoyo.trim()) {
                examples.push(example)
            }
        }
    }

    return examples
}

/**
 * Truncate text to maximum length with ellipsis
 */
function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) {
        return text
    }
    return text.slice(0, maxLength) + '...'
}
