import type { IExample, IExampleSegment } from '~/types/IExample'
import type { IExampleToken } from '~/types/IExampleToken'
import type { IStructuredExample } from '~/types/IStructuredExample'

function tokensToSegments(tokens: IExampleToken[]): { segments: IExampleSegment[]
    number?: string } {
    const segments: IExampleSegment[] = []
    let currentSegment: IExampleSegment | null = null
    let number: string | undefined
    let startIdx = 0

    const firstToken = tokens[0]
    const secondToken = tokens[1]
    if (tokens.length >= 2 && firstToken?.kind === 'ref' && secondToken?.kind === 'punct' && secondToken.value === ')') {
        number = firstToken.value
        startIdx = 2
    }

    const pushCurrent = () => {
        if (currentSegment && (currentSegment.turoyo?.trim() || currentSegment.translations.length)) {
            segments.push(currentSegment)
            currentSegment = null
        }
    }

    for (let i = startIdx; i < tokens.length; i++) {
        const token = tokens[i]
        if (!token) continue

        if (token.kind === 'turoyo') {
            const trimmedValue = token.value.trim()
            if (trimmedValue) {
                if (!currentSegment) {
                    currentSegment = {
                        turoyo: token.value,
                        translations: [],
                        references: [],
                    }
                }
                else if (currentSegment.translations.length > 0) {
                    const lastTranslation = currentSegment.translations[currentSegment.translations.length - 1]

                    const quotePairs = [
                        {
                            open: '\u2018',
                            close: '\u2019',
                        },
                        {
                            open: '"',
                            close: '"',
                        },
                        {
                            open: '\'',
                            close: '\'',
                        },
                    ]

                    let hasUnclosedQuote = false
                    if (lastTranslation) {
                        for (const pair of quotePairs) {
                            if (lastTranslation.includes(pair.open) && !lastTranslation.includes(pair.close)) {
                                hasUnclosedQuote = true
                                break
                            }
                        }
                    }

                    if (hasUnclosedQuote) {
                        currentSegment.translations[currentSegment.translations.length - 1] += token.value
                    }
                    else {
                        pushCurrent()
                        currentSegment = {
                            turoyo: token.value,
                            translations: [],
                            references: [],
                        }
                    }
                }
                else {
                    currentSegment.turoyo += token.value
                }
            }
        }
        else if (token.kind === 'translation') {
            if (!currentSegment) {
                currentSegment = {
                    turoyo: '',
                    translations: [],
                    references: [],
                }
            }
            currentSegment.translations.push(token.value)
        }
        else if (token.kind === 'punct' && token.value !== ';') {
            if (currentSegment) {
                if (currentSegment.translations.length > 0) {
                    currentSegment.translations[currentSegment.translations.length - 1] += token.value
                }
                else if (currentSegment.turoyo) {
                    currentSegment.turoyo += token.value
                }
            }
        }
        else if (token.kind === 'ref') {
            if (!currentSegment) {
                currentSegment = {
                    turoyo: '',
                    translations: [],
                    references: [],
                }
            }

            let refValue = token.value
            const prevToken = tokens[i - 1]
            if (prevToken?.kind === 'turoyo' && currentSegment.turoyo) {
                const turoyoTrimmed = currentSegment.turoyo.trim()
                const lastWord = turoyoTrimmed.split(/\s+/).pop()
                if (lastWord && /^[a-zA-Z]{1,4}$/.test(lastWord)) {
                    currentSegment.turoyo = turoyoTrimmed.slice(0, -lastWord.length).trim()
                    refValue = `${lastWord} ${refValue}`
                }
            }

            const nextToken = tokens[i + 1]
            if (nextToken?.kind === 'note') {
                currentSegment.references.push(`${refValue} ${nextToken.value}`)
                i++
            }
            else {
                currentSegment.references.push(refValue)
            }
        }
    }

    pushCurrent()
    return {
        segments,
        number: number ? `${number})` : undefined,
    }
}

export function segmentsToStructured(example: IExample): IStructuredExample {
    let segments: IExampleSegment[]
    let number: string | undefined

    if (example.segments) {
        segments = example.segments
    }
    else if (example.tokens) {
        const result = tokensToSegments(example.tokens)
        segments = result.segments
        number = result.number
    }
    else if (example.turoyo || example.translations?.length || example.references?.length) {
        segments = [{
            turoyo: example.turoyo || '',
            translations: example.translations || [],
            references: example.references || [],
        }]
    }
    else {
        segments = []
    }

    const items: IStructuredExample['items'] = []

    let current: { turoyo: string
        translation: string
        references: string[] } | null = null

    const pushCurrent = () => {
        if (!current) return
        const turoyo = (current.turoyo || '').trim()
        const translation = (current.translation || '').trim()
        const references = current.references.filter(Boolean)
        if (turoyo || translation || references.length) {
            items.push({
                turoyo,
                translation,
                references,
            })
        }
        current = null
    }

    const attachRefs = (refs: string[], notes?: string[]) => {
        if (!current) return
        if (notes && notes.length && refs.length) {
            const withNotes = `${notes.join(' ')}`
            const lastIdx = refs.length - 1
            const last = refs[lastIdx]
            if (last) {
                refs[lastIdx] = `${last} ${withNotes}`
            }
        }
        current.references.push(...refs)
    }

    for (const seg of segments) {
        const hasTuroyo = !!(seg.turoyo && seg.turoyo.trim())
        const hasTranslations = !!(seg.translations && seg.translations.length)
        const hasRefs = !!(seg.references && seg.references.length)

        if (hasTuroyo) {
            // New item starts at each turoyo-bearing segment
            pushCurrent()
            current = {
                turoyo: seg.turoyo.trim(),
                translation: hasTranslations ? seg.translations.join(' ') : '',
                references: [],
            }
            if (hasRefs) attachRefs(seg.references)
            continue
        }

        if (hasTranslations) {
            // Attach stray translation to current if exists
            if (!current) {
                current = {
                    turoyo: '',
                    translation: seg.translations.join(' '),
                    references: [],
                }
            }
            else {
                current.translation = [current.translation, seg.translations.join(' ')].filter(Boolean).join(' ')
            }
        }

        if (hasRefs) {
            attachRefs(seg.references, seg.notes)
        }
    }

    pushCurrent()

    return {
        number,
        items,
    }
}
