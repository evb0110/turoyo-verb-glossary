import type { Verb } from './verbs'
import { truncateText, tokenTextToString } from './textUtils'

interface Example {
    turoyo: string
    translations: string[]
    references: string[]
}

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

            if (example.turoyo && example.turoyo.trim()) {
                examples.push(example)
            }
        }
    }

    return examples
}

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

    if (verb.etymology?.etymons && verb.etymology.etymons.length > 0) {
        const etymonParts = verb.etymology.etymons.map((etymon) => {
            if (!etymon.source && etymon.raw) {
                return etymon.raw
            }

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

    for (const stem of verb.stems) {
        const stemParts: string[] = []

        const formsText = stem.forms.length > 0 ? stem.forms.join(', ') : '(no forms)'
        stemParts.push(`<div class="preview-stem-header"><strong>Stem ${stem.stem}:</strong> <span class="turoyo-text">${formsText}</span></div>`)

        if (stem.label_gloss_tokens && stem.label_gloss_tokens.length > 0) {
            const glossText = tokenTextToString(stem.label_gloss_tokens)
                .replace(/^(I{1,3}|IV|Pa\.|Af\.|Detransitive):\s*/i, '')
                .trim()

            if (glossText) {
                const truncatedGloss = truncateText(glossText, 100)
                stemParts.push(`<div class="preview-gloss">${truncatedGloss}</div>`)
            }
        }

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
