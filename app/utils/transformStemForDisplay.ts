import type { IStem } from '~/types/IStem'
import type { ITransformedStem } from '~/utils/ITransformedStem'
import { filterGlossTokens } from '~/utils/filterGlossTokens'

export function transformStemForDisplay(stem: IStem): ITransformedStem {
    const conjugationGroups = Object.entries(stem.conjugations || {}).map(([name, examples]) => ({
        name,
        examples,
    }))

    return {
        ...stem,
        exampleCount: conjugationGroups.reduce((count, group) => count + group.examples.length, 0),
        conjugationGroups,
        glossTokens: filterGlossTokens(stem.label_gloss_tokens || []),
    }
}
