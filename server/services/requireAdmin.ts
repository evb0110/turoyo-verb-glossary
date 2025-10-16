import type { H3Event } from 'h3'
import { auth } from '~~/server/lib/auth'
import { getUserById } from '~~/server/repositories/getUserById'
import { checkAdminRole } from '~~/server/services/checkAdminRole'

export async function requireAdmin(event: H3Event) {
    const session = await auth.api.getSession({ headers: event.headers })

    if (!session?.user) {
        throw createError({
            statusCode: 401,
            statusMessage: 'Unauthorized',
        })
    }

    const currentUser = await getUserById(session.user.id)

    const authResult = checkAdminRole(currentUser)

    if (!authResult.ok) {
        throw createError({
            statusCode: authResult.error === 'not_found' ? 404 : 403,
            statusMessage: authResult.error === 'not_found'
                ? 'User not found'
                : 'Forbidden: Admin access required',
        })
    }

    return authResult.data
}
