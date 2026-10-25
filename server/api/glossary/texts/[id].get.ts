import { getText } from '~~/server/repositories/glossary/getText'
import { textInContext } from '~~/server/services/glossary/textInContext'

export default defineEventHandler(async (event) => {
    const text = await getText(getRouterParam(event, 'id', { decode: true }) || '')
    if (!text) throw createError({
        statusCode: 404,
        message: 'Text not found.',
    })
    const value = getQuery(event).v
    if (value !== undefined) {
        const v = Number(value)
        if (!Number.isSafeInteger(v) || v < 0) throw createError({
            statusCode: 400,
            message: 'Invalid verse.',
        })
        return textInContext(text, v)
    }
    return text
})
