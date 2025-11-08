import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import { searchFullText } from '~~/server/services/searchFullText'

export default defineEventHandler(async (event) => {
    const {
        query,
        useRegex,
        caseSensitive,
        filters,
    } = await readBody<{
        query?: string
        useRegex?: boolean
        caseSensitive?: boolean
        filters?: Record<string, unknown> | null
    }>(event)

    if (!query) {
        throw createError({
            statusCode: 400,
            message: 'Invalid request: query required',
        })
    }

    const startedAt = Date.now()
    const result = await searchFullText(query, {
        useRegex,
        caseSensitive,
    })

    await logUserActivity(event, {
        eventType: 'search_fulltext',
        query,
        filters: filters && typeof filters === 'object' ? filters : null,
        resultCount: result.total,
        metadata: {
            useRegex: Boolean(useRegex),
            caseSensitive: Boolean(caseSensitive),
            durationMs: Date.now() - startedAt,
        },
    })

    return result
})
