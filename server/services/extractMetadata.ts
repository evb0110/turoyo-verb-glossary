import type { IVerb } from '~/types/IVerb'
import type { IVerbMetadata } from '~/types/IVerbMetadata'

export function extractMetadata(verb: IVerb): IVerbMetadata {
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
