import { getQuery } from 'h3'
import { getSessionActivity } from '~~/server/repositories/activity/getSessionActivity'
import { requireAdmin } from '~~/server/services/requireAdmin'
import type { IAdminSessionsResponse } from '#shared/types/IAdminSessionsResponse'

export default defineEventHandler<Promise<IAdminSessionsResponse>>(async (event) => {
    await requireAdmin(event)

    const query = getQuery(event)
    const limit = Math.min(Number(query.limit ?? 25), 100)
    const offset = Number(query.offset ?? 0)
    const search = typeof query.search === 'string' ? query.search : undefined
    const userId = typeof query.userId === 'string' ? query.userId : undefined

    return getSessionActivity({
        limit: Number.isFinite(limit) && limit > 0 ? limit : 25,
        offset: Number.isFinite(offset) && offset >= 0 ? offset : 0,
        search,
        userId,
    })
})
