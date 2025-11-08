import { and, count, desc, eq, ilike, or } from 'drizzle-orm'
import { db } from '~~/server/db'
import { user, userSessionActivity } from '~~/server/db/schema'
import type { IUserSessionActivity } from '#shared/types/IUserSessionActivity'

interface IGetSessionActivityParams {
    limit?: number
    offset?: number
    search?: string
    userId?: string
}

export async function getSessionActivity(
    params: IGetSessionActivityParams = {}
): Promise<{ sessions: IUserSessionActivity[]
    total: number }> {
    const {
        limit = 25,
        offset = 0,
        search,
        userId,
    } = params

    const filters = []

    if (userId) {
        filters.push(eq(userSessionActivity.userId, userId))
    }

    if (search) {
        const pattern = `%${search}%`
        filters.push(or(
            ilike(user.name, pattern),
            ilike(user.email, pattern),
            ilike(userSessionActivity.ipAddress, pattern),
            ilike(userSessionActivity.userAgent, pattern)
        ))
    }

    const whereClause = filters.length ? and(...filters) : undefined

    const baseListQuery = db.select({
        id: userSessionActivity.id,
        sessionId: userSessionActivity.sessionId,
        userId: userSessionActivity.userId,
        userName: user.name,
        userEmail: user.email,
        userRole: user.role,
        ipAddress: userSessionActivity.ipAddress,
        userAgent: userSessionActivity.userAgent,
        createdAt: userSessionActivity.createdAt,
        lastActivityAt: userSessionActivity.lastActivityAt,
        totalRequests: userSessionActivity.totalRequests,
        searchRequests: userSessionActivity.searchRequests,
        statsRequests: userSessionActivity.statsRequests,
        lastSearchQuery: userSessionActivity.lastSearchQuery,
        lastFilters: userSessionActivity.lastFilters,
    }).from(userSessionActivity)
        .leftJoin(user, eq(user.id, userSessionActivity.userId))

    const filteredListQuery = whereClause
        ? baseListQuery.where(whereClause)
        : baseListQuery

    const sessions = await filteredListQuery
        .orderBy(desc(userSessionActivity.lastActivityAt), desc(userSessionActivity.createdAt))
        .limit(limit)
        .offset(offset)

    const baseCountQuery = db.select({ value: count() }).from(userSessionActivity)
        .leftJoin(user, eq(user.id, userSessionActivity.userId))

    const filteredCountQuery = whereClause
        ? baseCountQuery.where(whereClause)
        : baseCountQuery

    const [totalResult] = await filteredCountQuery

    return {
        sessions: sessions as IUserSessionActivity[],
        total: Number(totalResult?.value ?? 0),
    }
}
