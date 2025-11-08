import { getQuery } from 'h3'
import { getActivityEvents } from '~~/server/repositories/activity/getActivityEvents'
import { requireAdmin } from '~~/server/services/requireAdmin'
import type { IAdminActivityResponse } from '#shared/types/IAdminActivityResponse'
import { activityEventTypes } from '#shared/config/activityEventTypes'

const isActivityEventType = (
    value: unknown
): value is typeof activityEventTypes[number] => {
    return typeof value === 'string'
        && activityEventTypes.includes(value as typeof activityEventTypes[number])
}

export default defineEventHandler<Promise<IAdminActivityResponse>>(async (event) => {
    await requireAdmin(event)

    const query = getQuery(event)
    const limit = Math.min(Number(query.limit ?? 25), 100)
    const offset = Number(query.offset ?? 0)
    const search = typeof query.search === 'string' ? query.search : undefined
    const userId = typeof query.userId === 'string' ? query.userId : undefined
    const sessionId = typeof query.sessionId === 'string' ? query.sessionId : undefined
    const eventType = isActivityEventType(query.eventType) ? query.eventType : undefined
    const host = typeof query.host === 'string' ? query.host : undefined

    return getActivityEvents({
        limit: Number.isFinite(limit) && limit > 0 ? limit : 25,
        offset: Number.isFinite(offset) && offset >= 0 ? offset : 0,
        search,
        userId,
        sessionId,
        eventType,
        host,
    })
})
