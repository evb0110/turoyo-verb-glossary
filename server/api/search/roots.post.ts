import { searchRoots } from '~~/server/services/searchRoots'

export default defineEventHandler(async (event) => {
    const {
        query,
        useRegex,
        caseSensitive,
    } = await readBody(event)

    if (!query) {
        throw createError({
            statusCode: 400,
            message: 'Invalid request: query required',
        })
    }

    return searchRoots(query, {
        useRegex,
        caseSensitive,
    })
})
