import type { Stem } from '~/types/verb'

export interface GlossToken {
    italic: boolean
    text: string
}

export interface ConjugationGroup {
    name: string
    examples: Array<{
        turoyo: string
        translations: string[]
        references: string[]
    }>
}

export interface TransformedStem extends Stem {
    exampleCount: number
    conjugationGroups: ConjugationGroup[]
    glossTokens: GlossToken[]
}

export function filterGlossTokens(tokens: GlossToken[]): GlossToken[] {
    if (!Array.isArray(tokens)) return []

    return tokens.filter((t, idx, arr) => {
        const first = arr[0]?.text?.trim() || ''

        if (idx === 0 && /^[IVX]+\s*:/.test(first)) return false
        return true
    })
}

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
