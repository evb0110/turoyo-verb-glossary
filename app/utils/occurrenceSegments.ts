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
    // The analyses of one form are listed in verse order, so the n-th match of the form gets the n-th
    // analysis (in PrS 32/3 the first ḥzele finds a cave, the second sees the giant). Matches beyond the
    // analyses keep the last one. Longer forms go first, so a short form inside a longer one is skipped.
    const byForm = new Map<string, IOccurrence[]>()
    for (const occurrence of occurrences) {
        const form = normalizeTuroyo(occurrence.form)
        if (form) byForm.set(form, [...(byForm.get(form) || []), occurrence])
    }
    for (const [form, analyses] of [...byForm].toSorted(([a], [b]) => b.length - a.length)) {
        let matched = 0
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
                occurrence: analyses[Math.min(matched++, analyses.length - 1)]!,
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
