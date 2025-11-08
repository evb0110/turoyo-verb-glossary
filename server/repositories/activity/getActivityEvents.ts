import { and, count, desc, eq, ilike, or } from 'drizzle-orm'
import { db } from '~~/server/db'
import { user, userActivityLog, userSessionActivity } from '~~/server/db/schema'
import type { TActivityEventType } from '#shared/config/activityEventTypes'
import type { IUserActivityLog } from '#shared/types/IUserActivityLog'
import { activityEventTypes } from '#shared/config/activityEventTypes'

interface IGetActivityEventsParams {
    limit?: number
    offset?: number
    search?: string
    userId?: string
    sessionId?: string
    eventType?: TActivityEventType
    host?: string
}

export async function getActivityEvents(
    params: IGetActivityEventsParams = {}
): Promise<{
    events: IUserActivityLog[]
    total: number
    counts: Record<TActivityEventType, number>
}> {
    const {
        limit = 25,
        offset = 0,
        search,
        userId,
        sessionId,
        eventType,
        host,
    } = params

    const filters = []

    if (userId) {
        filters.push(eq(userActivityLog.userId, userId))
    }

    if (sessionId) {
        filters.push(eq(userSessionActivity.sessionId, sessionId))
    }

    if (eventType) {
        filters.push(eq(userActivityLog.eventType, eventType))
    }

    if (host) {
        filters.push(eq(userActivityLog.host, host))
    }

    if (search) {
        const pattern = `%${search}%`
        filters.push(or(
            ilike(user.name, pattern),
            ilike(user.email, pattern),
            ilike(userActivityLog.query, pattern)
        ))
    }

    const whereClause = filters.length ? and(...filters) : undefined

    const baseListQuery = db.select({
        id: userActivityLog.id,
        host: userActivityLog.host,
        userId: userActivityLog.userId,
        userName: user.name,
        userEmail: user.email,
        userRole: user.role,
        sessionActivityId: userActivityLog.sessionActivityId,
        sessionId: userSessionActivity.sessionId,
        eventType: userActivityLog.eventType,
        path: userActivityLog.path,
        query: userActivityLog.query,
        filters: userActivityLog.filters,
        resultCount: userActivityLog.resultCount,
        metadata: userActivityLog.metadata,
        statusCode: userActivityLog.statusCode,
        createdAt: userActivityLog.createdAt,
    }).from(userActivityLog)
        .leftJoin(userSessionActivity, eq(userSessionActivity.id, userActivityLog.sessionActivityId))
        .leftJoin(user, eq(user.id, userActivityLog.userId))

    const filteredListQuery = whereClause
        ? baseListQuery.where(whereClause)
        : baseListQuery

    const events = await filteredListQuery
        .orderBy(desc(userActivityLog.createdAt))
        .limit(limit)
        .offset(offset)

    const baseCountQuery = db.select({ value: count() }).from(userActivityLog)
        .leftJoin(userSessionActivity, eq(userSessionActivity.id, userActivityLog.sessionActivityId))
        .leftJoin(user, eq(user.id, userActivityLog.userId))

    const filteredCountQuery = whereClause
        ? baseCountQuery.where(whereClause)
        : baseCountQuery

    const [totalResult] = await filteredCountQuery

    const baseSummaryQuery = db.select({
        eventType: userActivityLog.eventType,
        value: count(),
    }).from(userActivityLog)
        .leftJoin(userSessionActivity, eq(userSessionActivity.id, userActivityLog.sessionActivityId))
        .leftJoin(user, eq(user.id, userActivityLog.userId))
        .groupBy(userActivityLog.eventType)

    const filteredSummaryQuery = whereClause
        ? baseSummaryQuery.where(whereClause)
        : baseSummaryQuery

    const summaryRows = await filteredSummaryQuery
    const counts = Object.fromEntries(
        activityEventTypes.map(type => [type, 0])
    ) as Record<TActivityEventType, number>

    for (const row of summaryRows) {
        counts[row.eventType as TActivityEventType] = Number(row.value ?? 0)
    }

    return {
        events: events as IUserActivityLog[],
        total: Number(totalResult?.value ?? 0),
        counts,
    }
}
