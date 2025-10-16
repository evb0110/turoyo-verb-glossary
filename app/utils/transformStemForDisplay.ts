import type { IStem } from '~/types/IStem'
import type { ITransformedStem } from '~/types/ITransformedStem'
import { filterGlossTokens } from '~/utils/filterGlossTokens'

export function transformStemForDisplay(stem: IStem): ITransformedStem {
    const conjugationGroups = Object.entries(stem.conjugations || {}).map(([name, examples]) => ({
        name,
        examples,
    }))

    const glossTokens = filterGlossTokens(stem.label_gloss_tokens || [])
    const hasGlossInfo = glossTokens.length > 0 || !!stem.label_raw
    const formsStr = stem.forms?.length ? stem.forms.join('/') : 'No recorded forms'
    const formsListDisplay = stem.forms?.length ? stem.forms.join(', ') : 'No recorded forms'
    const exampleCount = conjugationGroups.reduce((count, group) => count + group.examples.length, 0)

    return {
        ...stem,
        exampleCount,
        conjugationGroups,
        glossTokens,
        hasGlossInfo,
        stemLabel: `${stem.stem}: ${formsStr}`,
        formsListDisplay,
        hasExamples: exampleCount > 0,
    }
}
