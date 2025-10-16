import { auth } from '~~/server/lib/auth'
import { updateUserRole } from '~~/server/repositories/updateUserRole'
import { requireAdmin } from '~~/server/services/requireAdmin'
import type { IUserActionResponse } from '~~/server/types/IUserActionResponse'

export default defineEventHandler<Promise<IUserActionResponse>>(async (event) => {
    await requireAdmin(event)

    const session = await auth.api.getSession({
        headers: event.headers,
    })

    const userId = getRouterParam(event, 'id')

    if (!userId) {
        throw createError({
            statusCode: 400,
            statusMessage: 'User ID is required',
        })
    }

    if (userId === session?.user?.id) {
        throw createError({
            statusCode: 400,
            statusMessage: 'Cannot block yourself',
        })
    }

    const updated = await updateUserRole(userId, 'blocked')

    if (!updated) {
        throw createError({
            statusCode: 404,
            statusMessage: 'User not found',
        })
    }

    return {
        success: true,
        user: updated,
    }
})
