import { getAllTexts } from '~~/server/repositories/glossary/getAllTexts'
import { collectResearchNotes } from '~~/server/services/glossary/collectResearchNotes'
import { pageResearchNotes } from '~~/server/services/glossary/pageResearchNotes'

export default defineEventHandler(async (event) => {
    const query = getQuery(event)
    return pageResearchNotes(
        collectResearchNotes(await getAllTexts()),
        String(query.question || ''),
        String(query.root || ''),
        Number(query.page || 1)
    )
})
