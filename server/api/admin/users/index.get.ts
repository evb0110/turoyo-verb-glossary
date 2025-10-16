import { requireAdmin } from '~~/server/services/requireAdmin'
import { getAllUsers } from '~~/server/repositories/getAllUsers'

export default defineEventHandler(async (event) => {
    await requireAdmin(event)

    const users = await getAllUsers()

    return users
})
