import type { IVerb } from '~/types/IVerb'
import type { IExcerpt } from '~/types/IExcerpt'
import { createSearchRegex, matchAll } from '~~/server/utils/regexSearch'
import { extractContext, tokenTextToString } from '~~/server/utils/textUtils'

function addExcerpt(
    excerpts: IExcerpt[],
    seenTexts: Set<string>,
    excerptText: string,
    excerpt: Omit<IExcerpt, 'text'>
) {
    if (!seenTexts.has(excerptText)) {
        seenTexts.add(excerptText)
        excerpts.push({
            ...excerpt,
            text: excerptText
        })
    }
}

export function generateExcerpts(
    verb: IVerb,
    query: string,
    opts: {
        useRegex?: boolean
        caseSensitive?: boolean
        maxExcerpts?: number
    } = {}
): IExcerpt[] {
    const excerpts: IExcerpt[] = []
    const regex = createSearchRegex(query, opts)
    if (!regex) {
        return excerpts // Invalid regex, return empty
    }

    const maxExcerpts = opts.maxExcerpts ?? 5
    const seenTexts = new Set<string>() // Track unique texts to avoid duplicates

    if (verb.lemma_header_tokens) {
        const headerText = tokenTextToString(verb.lemma_header_tokens)

        for (const match of matchAll(headerText, regex)) {
            if (excerpts.length >= maxExcerpts) break

            const excerptText = extractContext(headerText, match.index, match[0].length, 60)
            addExcerpt(excerpts, seenTexts, excerptText, {
                type: 'etymology',
                html: excerptText,
                label: 'Citation:'
            })
        }
    }

    for (const stem of verb.stems) {
        for (const form of stem.forms) {
            if (regex.test(form)) {
                addExcerpt(excerpts, seenTexts, form, {
                    type: 'form',
                    stem: stem.stem,
                    html: form,
                    label: `Form (Stem ${stem.stem})`
                })
            }
        }

        if (stem.label_gloss_tokens) {
            const glossText = tokenTextToString(stem.label_gloss_tokens)

            for (const match of matchAll(glossText, regex)) {
                if (excerpts.length >= maxExcerpts) break

                const excerptText = extractContext(glossText, match.index, match[0].length, 60)
                addExcerpt(excerpts, seenTexts, excerptText, {
                    type: 'gloss',
                    stem: stem.stem,
                    html: excerptText,
                    label: `Meaning (Stem ${stem.stem}):`
                })
            }
        }

        for (const [conjType, examples] of Object.entries(stem.conjugations)) {
            for (const example of examples) {
                if (excerpts.length >= maxExcerpts) {
                    return excerpts
                }

                if (example.turoyo) {
                    const tMatch = example.turoyo.match(regex)
                    if (tMatch && tMatch.index !== undefined) {
                        const excerptText = extractContext(example.turoyo, tMatch.index, tMatch[0].length, 60)
                        addExcerpt(excerpts, seenTexts, excerptText, {
                            type: 'example',
                            stem: stem.stem,
                            conjugationType: conjType,
                            html: excerptText,
                            label: `${conjType}:`
                        })
                    }
                }

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
                                html: excerptText,
                                label: `Translation:`
                            })
                        }
                    }
                }
            }
        }
    }

    if (verb.etymology && Array.isArray(verb.etymology.etymons)) {
        for (const etymon of verb.etymology.etymons) {
            if (excerpts.length >= maxExcerpts) {
                break
            }

            const searchFields = [
                etymon.meaning,
                etymon.notes,
                etymon.raw,
                etymon.source_root
            ].filter((field): field is string => Boolean(field)) // Type-safe filter

            for (const field of searchFields) {
                for (const match of matchAll(field, regex)) {
                    if (excerpts.length >= maxExcerpts) break

                    const excerptText = extractContext(field, match.index, match[0].length, 60)
                    addExcerpt(excerpts, seenTexts, excerptText, {
                        type: 'etymology',
                        html: excerptText,
                        label: `Etymology:`
                    })
                }
            }
        }
    }

    return excerpts.slice(0, maxExcerpts)
}
