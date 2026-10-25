import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import { summarizeGlossary } from '~~/server/services/glossary/summarizeGlossary'

export default defineEventHandler(async (event) => {
    const stats = summarizeGlossary(await getGlossaryCatalog())
    await logUserActivity(event, {
        eventType: 'view_stats',
        resultCount: stats.entries,
    })
    return stats
})
