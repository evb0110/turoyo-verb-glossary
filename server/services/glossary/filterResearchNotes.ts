import type { collectResearchNotes } from '~~/server/services/glossary/collectResearchNotes'
import { researchQuestion } from '~~/server/services/glossary/researchQuestion'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

// The notes whose root starts with `root` (all notes when it is empty), and those of them tagged with `question`.
export function filterResearchNotes(notes: ReturnType<typeof collectResearchNotes>, question: string, root: string) {
    const rootQuery = normalizeTuroyo(root.trim())
    const byRoot = rootQuery ? notes.filter(note => normalizeTuroyo(note.occurrence.root).startsWith(rootQuery)) : notes
    return {
        byRoot,
        matching: question
            ? byRoot.filter(note => note.occurrence.rq.some(tag => researchQuestion(tag) === question))
            : byRoot,
    }
}
