import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { getTextIndex } from '~~/server/repositories/glossary/getTextIndex'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import { summarizeGlossary } from '~~/server/services/glossary/summarizeGlossary'

export default defineEventHandler(async (event) => {
    const stats = summarizeGlossary(await getEntryIndex(), await getTextIndex(), await getProposalIndex())
    await logUserActivity(event, {
        eventType: 'view_stats',
        resultCount: stats.entries,
    })
    return stats
})
