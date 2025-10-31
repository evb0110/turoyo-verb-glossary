import { getAuth } from '~~/server/lib/auth'

export default defineEventHandler(async (event) => {
    try {
        const auth = getAuth(event)
        return await auth.handler(toWebRequest(event))
    }
    catch (error) {
        console.error('Auth endpoint error:', error)
        throw createError({
            statusCode: 500,
            message: error instanceof Error ? error.message : 'Authentication error',
            data: { error: String(error) },
        })
    }
})
