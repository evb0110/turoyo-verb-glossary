import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import { searchGlossary } from '~~/server/services/glossary/searchGlossary'

export default defineEventHandler(async (event) => {
    const query = getQuery(event)
    const q = String(query.q || '').trim()
    if (!q) return {
        results: [],
        counts: {},
        total: 0,
    }
    try {
        const result = searchGlossary((await getGlossaryCatalog()).search, q, query.regex === 'true')
        await logUserActivity(event, {
            eventType: 'search_fulltext',
            query: q,
            resultCount: result.total,
            filters: { regex: query.regex === 'true' },
        })
        return result
    }
    catch (error) {
        throw createError({
            statusCode: 400,
            message: error instanceof Error ? error.message : 'Invalid expression.',
        })
    }
})
