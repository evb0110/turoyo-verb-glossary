import { getAllUsers } from '~~/server/repositories/auth/getAllUsers'
import { requireApproved } from '~~/server/services/auth/requireApproved'

export default defineEventHandler(async (event) => {
    const user = await requireApproved(event)
    if (user.role !== 'admin') throw createError({
        statusCode: 403,
        message: 'Admin access required.',
    })

    const users = await getAllUsers()

    return users
})
