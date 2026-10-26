import { getEntry } from '~~/server/repositories/glossary/getEntry'
import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getTextIndex } from '~~/server/repositories/glossary/getTextIndex'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'

export default defineEventHandler(async (event) => {
    const id = getRouterParam(event, 'id', { decode: true }) || ''
    const entry = await getEntry(id)
    const proposals = await getEntryProposals(id)
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
        textIds: (await getTextIndex()).map(text => text.id),
    }
})
