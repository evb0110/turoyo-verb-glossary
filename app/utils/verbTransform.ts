/**
 * Verb transformation utilities for display formatting
 */

import type { Stem } from '~/types/verb'

/**
 * Token with optional italic formatting
 */
export interface GlossToken {
    italic: boolean
    text: string
}

/**
 * Conjugation group with name and examples
 */
export interface ConjugationGroup {
    name: string
    examples: Array<{
        turoyo: string
        translations: string[]
        references: string[]
    }>
}

/**
 * Transformed stem for display with computed properties
 */
export interface TransformedStem extends Stem {
    exampleCount: number
    conjugationGroups: ConjugationGroup[]
    glossTokens: GlossToken[]
}

/**
 * Filter gloss tokens to remove stem prefix (e.g., "I:", "II:")
 * @param tokens - Array of gloss tokens
 * @returns Filtered tokens without stem prefix
 */
export function filterGlossTokens(tokens: GlossToken[]): GlossToken[] {
    if (!Array.isArray(tokens)) return []

    return tokens.filter((t, idx, arr) => {
        const first = arr[0]?.text?.trim?.() || ''
        // Remove first token if it matches Roman numeral stem notation
        if (idx === 0 && /^[IVX]+\s*:/.test(first)) return false
        return true
    })
}

/**
 * Transform a stem for display with computed properties
 * @param stem - The stem to transform
 * @returns Transformed stem with conjugation groups and filtered gloss tokens
 */
export function transformStemForDisplay(stem: Stem): TransformedStem {
    const conjugationGroups = Object.entries(stem.conjugations || {}).map(([name, examples]) => ({
        name,
        examples
    }))

    return {
        ...stem,
        exampleCount: conjugationGroups.reduce((count, group) => count + group.examples.length, 0),
        conjugationGroups,
        glossTokens: filterGlossTokens(stem.label_gloss_tokens || [])
    }
}
