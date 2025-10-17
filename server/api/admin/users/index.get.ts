import { getAllUsers } from '~~/server/repositories/auth/getAllUsers'
import { requireAdmin } from '~~/server/services/requireAdmin'

export default defineEventHandler(async (event) => {
    await requireAdmin(event)

    const users = await getAllUsers()

    return users
})
