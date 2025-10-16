import { searchFullText } from '~~/server/services/searchFullText'

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

    return searchFullText(query, {
        useRegex,
        caseSensitive,
    })
})
