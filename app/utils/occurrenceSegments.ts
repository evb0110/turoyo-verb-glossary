import type { IOccurrence } from '#shared/types/IOccurrence'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

export function occurrenceSegments(text: string, occurrences: IOccurrence[]) {
    const offsets: number[] = []
    const units = [...text.matchAll(/\P{M}\p{M}*|\p{M}+/gu)]
    for (const unit of units) for (const _char of normalizeTuroyo(unit[0])) offsets.push(unit.index)
    const normalized = normalizeTuroyo(text)
    const hits: Array<{ start: number
        end: number
        occurrence: IOccurrence }> = []
    for (const occurrence of occurrences.toSorted((a, b) => b.form.length - a.form.length)) {
        const form = normalizeTuroyo(occurrence.form)
        if (!form) continue
        let pos = normalized.indexOf(form)
        while (pos !== -1) {
            const start = offsets[pos] ?? pos
            const end = offsets[pos + form.length] ?? text.length
            const previous = normalized[pos - 1] || ''
            const following = normalized[pos + form.length] || ''
            if (!/[\p{L}\p{M}]/u.test(previous) && !/[\p{L}\p{M}]/u.test(following)
                && !hits.some(hit => start < hit.end && end > hit.start)) hits.push({
                start,
                end,
                occurrence,
            })
            pos = normalized.indexOf(form, pos + form.length)
        }
    }
    const segments: Array<{ text: string
        occurrence?: IOccurrence }> = []
    let cursor = 0
    for (const hit of hits.toSorted((a, b) => a.start - b.start)) {
        if (hit.start > cursor) segments.push({ text: text.slice(cursor, hit.start) })
        segments.push({
            text: text.slice(hit.start, hit.end),
            occurrence: hit.occurrence,
        })
        cursor = hit.end
    }
    if (cursor < text.length) segments.push({ text: text.slice(cursor) })
    return segments
}
