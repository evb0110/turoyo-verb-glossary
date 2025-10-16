import type { IVerb } from '~/types/IVerb'
import type { IExcerpt } from '~/types/IExcerpt'
import { createSearchRegex } from '~~/server/utils/createSearchRegex'
import { matchAll } from '~~/server/utils/matchAll'
import { extractContext } from '~~/server/utils/extractContext'
import { tokenTextToString } from '~~/server/utils/tokenTextToString'

function shouldAddExcerpt(excerptText: string, seenTexts: Set<string>): boolean {
    return !seenTexts.has(excerptText)
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
        return excerpts
    }

    const maxExcerpts = opts.maxExcerpts ?? 5
    const seenTexts = new Set<string>()

    if (verb.lemma_header_tokens) {
        const headerText = tokenTextToString(verb.lemma_header_tokens)

        for (const match of matchAll(headerText, regex)) {
            if (excerpts.length >= maxExcerpts) break

            const excerptText = extractContext(headerText, match.index, match[0].length, 60)
            if (shouldAddExcerpt(excerptText, seenTexts)) {
                seenTexts.add(excerptText)
                excerpts.push({
                    type: 'etymology',
                    html: excerptText,
                    label: 'Citation:',
                    text: excerptText
                })
            }
        }
    }

    for (const stem of verb.stems) {
        for (const form of stem.forms) {
            if (regex.test(form)) {
                if (shouldAddExcerpt(form, seenTexts)) {
                    seenTexts.add(form)
                    excerpts.push({
                        type: 'form',
                        stem: stem.stem,
                        html: form,
                        label: `Form (Stem ${stem.stem})`,
                        text: form
                    })
                }
            }
        }

        if (stem.label_gloss_tokens) {
            const glossText = tokenTextToString(stem.label_gloss_tokens)

            for (const match of matchAll(glossText, regex)) {
                if (excerpts.length >= maxExcerpts) break

                const excerptText = extractContext(glossText, match.index, match[0].length, 60)
                if (shouldAddExcerpt(excerptText, seenTexts)) {
                    seenTexts.add(excerptText)
                    excerpts.push({
                        type: 'gloss',
                        stem: stem.stem,
                        html: excerptText,
                        label: `Meaning (Stem ${stem.stem}):`,
                        text: excerptText
                    })
                }
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
                        if (shouldAddExcerpt(excerptText, seenTexts)) {
                            seenTexts.add(excerptText)
                            excerpts.push({
                                type: 'example',
                                stem: stem.stem,
                                conjugationType: conjType,
                                html: excerptText,
                                label: `${conjType}:`,
                                text: excerptText
                            })
                        }
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
                            if (shouldAddExcerpt(excerptText, seenTexts)) {
                                seenTexts.add(excerptText)
                                excerpts.push({
                                    type: 'translation',
                                    stem: stem.stem,
                                    conjugationType: conjType,
                                    html: excerptText,
                                    label: `Translation:`,
                                    text: excerptText
                                })
                            }
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
            ].filter((field): field is string => Boolean(field))

            for (const field of searchFields) {
                for (const match of matchAll(field, regex)) {
                    if (excerpts.length >= maxExcerpts) break

                    const excerptText = extractContext(field, match.index, match[0].length, 60)
                    if (shouldAddExcerpt(excerptText, seenTexts)) {
                        seenTexts.add(excerptText)
                        excerpts.push({
                            type: 'etymology',
                            html: excerptText,
                            label: `Etymology:`,
                            text: excerptText
                        })
                    }
                }
            }
        }
    }

    return excerpts.slice(0, maxExcerpts)
}
