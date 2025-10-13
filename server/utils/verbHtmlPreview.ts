/**
 * Server-side utilities for generating HTML previews of verb articles
 * Used for "roots only" search mode to show full article previews
 */

import type { Verb } from './verbs'
import { truncateText, tokenTextToString } from './textUtils'

interface Example {
    turoyo: string
    translations: string[]
    references: string[]
}

/**
 * Collect examples from conjugations, up to a maximum count
 * Internal helper for generateFullPreview
 *
 * @param conjugations - Conjugation data from a stem
 * @param maxCount - Maximum number of examples to collect
 * @returns Array of examples with turoyo text, translations, and references
 */
function collectExamples(
    conjugations: { [key: string]: Example[] },
    maxCount: number
): Example[] {
    const examples: Example[] = []

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
 * Generate full article preview for root search mode
 * Shows etymology, stems with forms, glosses, and sample examples
 *
 * @param verb - The verb to generate a preview for
 * @param opts - Preview generation options
 * @returns HTML string with formatted preview content
 *
 * @example
 * const previewHtml = generateFullPreview(verb, {
 *   maxExamplesPerStem: 3,
 *   maxExampleLength: 150
 * })
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
    if (verb.etymology?.etymons && verb.etymology.etymons.length > 0) {
        const etymonParts = verb.etymology.etymons.map((etymon) => {
            // For raw-only etymons (no structured source), display the raw text
            if (!etymon.source && etymon.raw) {
                return etymon.raw
            }

            // For structured etymons, format nicely
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
            const glossText = tokenTextToString(stem.label_gloss_tokens)
                .replace(/^(I{1,3}|IV|Pa\.|Af\.|Detransitive):\s*/i, '') // Remove stem label prefix
                .trim()

            if (glossText) {
                const truncatedGloss = truncateText(glossText, 100)
                stemParts.push(`<div class="preview-gloss">${truncatedGloss}</div>`)
            }
        }

        // Sample examples
        const examples = collectExamples(stem.conjugations, maxExamplesPerStem)

        if (examples.length > 0) {
            const exampleItems = examples.map((ex) => {
                const turoyo = truncateText(ex.turoyo, maxExampleLength)
                const translation = ex.translations[0]
                    ? truncateText(ex.translations[0], maxExampleLength)
                    : ''
                const refs = ex.references[0]
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
