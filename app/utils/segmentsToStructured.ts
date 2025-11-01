import type { IExample, IExampleSegment } from '~/types/IExample'
import type { IStructuredExample } from '~/types/IStructuredExample'

function stripLeadingParen(text: string) {
    return text.startsWith(')') ? text.slice(1).trimStart() : text
}

export function segmentsToStructured(example: IExample): IStructuredExample {
    const segments = example.segments || []
    const items: IStructuredExample['items'] = []

    let number: string | undefined
    let first = segments[0]

    if (first) {
        const digitRefIndex = first.references?.findIndex(r => /^\d+$/.test(r)) ?? -1
        if (digitRefIndex >= 0) {
            number = `${first.references![digitRefIndex]})`
            first = {
                ...first,
                turoyo: stripLeadingParen(first.turoyo || ''),
                references: first.references!.filter((_, i) => i !== digitRefIndex),
            }
        }
    }

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
        if (notes && notes.length) {
            // Append notes to the last ref (e.g., "21/65 [MT]") to avoid losing information
            const withNotes = notes.length ? `${notes.join(' ')}` : ''
            if (refs.length) {
                const last = refs[refs.length - 1]
                refs[refs.length - 1] = withNotes ? `${last} ${withNotes}` : last
            }
        }
        current.references.push(...refs)
    }

    const allSegments: IExampleSegment[] = first ? [first, ...segments.slice(1)] : segments

    for (const seg of allSegments) {
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
