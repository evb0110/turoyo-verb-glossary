import { updateUserRole } from '~~/server/repositories/updateUserRole'
import { requireAdmin } from '~~/server/services/requireAdmin'
import type { IUserActionResponse } from '~~/server/types/IUserActionResponse'

export default defineEventHandler<Promise<IUserActionResponse>>(async (event) => {
    await requireAdmin(event)

    const userId = getRouterParam(event, 'id')

    if (!userId) {
        throw createError({
            statusCode: 400,
            statusMessage: 'User ID is required',
        })
    }

    const updated = await updateUserRole(userId, 'user')

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
