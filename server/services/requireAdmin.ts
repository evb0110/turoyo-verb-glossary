import type { H3Event } from 'h3'
import { auth } from '~~/server/lib/auth'
import { getUserById } from '~~/server/repositories/getUserById'

export async function requireAdmin(event: H3Event) {
    const session = await auth.api.getSession({ headers: event.headers })

    if (!session?.user) {
        throw createError({
            statusCode: 401,
            statusMessage: 'Unauthorized'
        })
    }

    const currentUser = await getUserById(session.user.id)

    if (!currentUser || currentUser.role !== 'admin') {
        throw createError({
            statusCode: 403,
            statusMessage: 'Forbidden: Admin access required'
        })
    }

    return currentUser
}
