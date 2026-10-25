import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'

export default defineEventHandler(async (event) => {
    const id = getRouterParam(event, 'id', { decode: true }) || ''
    const catalog = await getGlossaryCatalog()
    const entry = catalog.entries.find(entry => entry.id === id) || null
    const proposals = catalog.proposals.filter(proposal => proposal.entryId === id)
    if (!entry && !proposals.some(proposal => proposal.kind === 'new-root')) {
        throw createError({
            statusCode: 404,
            message: 'Entry not found.',
        })
    }
    await logUserActivity(event, {
        eventType: 'view_verb',
        query: id,
        resultCount: 1,
    })
    return {
        entry,
        proposals,
        textIds: catalog.textIndex.map(text => text.id),
    }
})
