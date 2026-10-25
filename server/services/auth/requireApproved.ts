import { getCurrentUser } from '~~/server/repositories/auth/getCurrentUser'
import type { H3Event } from 'h3'

export async function requireApproved(event: H3Event) {
    const user = await getCurrentUser(event)
    if (!user) throw createError({
        statusCode: 401,
        message: 'Sign in to continue.',
    })
    if (user.role !== 'admin' && user.role !== 'user') {
        throw createError({
            statusCode: 403,
            message: 'Your account must be approved.',
        })
    }
    return user
}
