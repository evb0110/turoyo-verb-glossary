import type { collectResearchNotes } from '~~/server/services/glossary/collectResearchNotes'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

const PAGE_SIZE = 100

// The readers tag the same question as "RQ-aspect" or "aspect"; both count as "aspect".
function questionName(tag: string) {
    return tag.replace(/^RQ-/iu, '').toLowerCase()
}

// One page of research notes for a question and/or root, with the count for every question.
export function pageResearchNotes(
    notes: ReturnType<typeof collectResearchNotes>,
    question: string,
    root: string,
    page: number
) {
    const rootQuery = normalizeTuroyo(root.trim())
    const byRoot = rootQuery ? notes.filter(note => normalizeTuroyo(note.occurrence.root).startsWith(rootQuery)) : notes
    const counts = new Map<string, number>()
    for (const note of byRoot)
        for (const name of new Set(note.occurrence.rq.map(questionName)))
            counts.set(name, (counts.get(name) || 0) + 1)
    const matching = question
        ? byRoot.filter(note => note.occurrence.rq.some(tag => questionName(tag) === question))
        : byRoot
    const pages = Math.max(1, Math.ceil(matching.length / PAGE_SIZE))
    const current = Math.min(Math.max(1, Math.trunc(page) || 1), pages)
    return {
        total: matching.length,
        all: byRoot.length,
        page: current,
        pages,
        questions: [...counts].map(([name, count]) => ({
            name,
            count,
        })).toSorted((a, b) => a.name.localeCompare(b.name)),
        notes: matching.slice((current - 1) * PAGE_SIZE, current * PAGE_SIZE).map(note => ({
            ...note,
            questions: [...new Set(note.occurrence.rq.map(questionName))],
        })),
    }
}
