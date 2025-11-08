import { randomUUID } from 'node:crypto'
import { eq, sql } from 'drizzle-orm'
import { getRequestHeader, getRequestURL } from 'h3'
import { db } from '~~/server/db'
import { userActivityLog, userSessionActivity } from '~~/server/db/schema'
import { auth } from '~~/server/lib/auth'
import type { TActivityEventType } from '#shared/config/activityEventTypes'
import type { H3Event } from 'h3'

export interface ILogUserActivityInput {
    eventType: TActivityEventType
    query?: string | null
    filters?: Record<string, unknown> | null
    resultCount?: number | null
    metadata?: Record<string, unknown> | null
    statusCode?: number
    path?: string | null
}

function getClientIp(event: H3Event) {
    const forwarded = getRequestHeader(event, 'x-forwarded-for')
    if (forwarded) {
        const [ip] = forwarded.split(',').map(part => part.trim()).filter(Boolean)
        if (ip) return ip
    }

    return event.node.req.socket.remoteAddress || null
}

function normalizeHost(requestUrl: URL) {
    const {
        hostname,
        port,
    } = requestUrl
    if (!hostname) return null

    // Strip common provider prefixes
    const vercelMatch = hostname.match(/(?:^|\.)vercel\.app$/u)
    if (vercelMatch) {
        return 'vercel'
    }

    const cfMatch = hostname.match(/(?:^|\.)workers\.dev$/u)
    if (cfMatch) {
        return 'cloudflare'
    }

    // collapse anything like subdomain.domain.tld → domain.tld
    const parts = hostname.split('.')
    if (parts.length > 2) {
        return parts.slice(-2).join('.') + (port ? `:${port}` : '')
    }

    return port ? `${hostname}:${port}` : hostname
}

export async function logUserActivity(
    event: H3Event,
    input: ILogUserActivityInput
) {
    try {
        const session = await auth.api.getSession({ headers: event.headers })

        if (!session?.user || !session.session) {
            return
        }

        const now = new Date()
        const requestUrl = getRequestURL(event)
        const clientPathHeader = getRequestHeader(event, 'x-client-path') ?? null
        const clientUrl = clientPathHeader
            ? new URL(clientPathHeader, `${requestUrl.protocol}//${requestUrl.host}`)
            : null
        const ipAddress = getClientIp(event)
        const userAgent = getRequestHeader(event, 'user-agent') ?? null
        const effectiveUrl = clientUrl ?? requestUrl
        const path = input.path ?? effectiveUrl.pathname ?? requestUrl.pathname
        const host = normalizeHost(effectiveUrl) ?? requestUrl.host
        const metadataPayload = {
            ...(input.metadata ?? {}),
            ...(clientUrl?.search ? { pageQuery: clientUrl.search } : {}),
        }

        const [sessionRecord] = await db.insert(userSessionActivity).values({
            id: randomUUID(),
            sessionId: session.session.id,
            userId: session.user.id,
            ipAddress,
            userAgent,
        }).onConflictDoUpdate({
            target: userSessionActivity.sessionId,
            set: {
                userId: session.user.id,
                ipAddress,
                userAgent,
                lastActivityAt: now,
            },
        }).returning({ id: userSessionActivity.id })

        const sessionActivityId = sessionRecord?.id

        if (!sessionActivityId) {
            return
        }

        await db.insert(userActivityLog).values({
            id: randomUUID(),
            userId: session.user.id,
            sessionActivityId,
            eventType: input.eventType,
            host,
            path,
            query: input.query ?? null,
            filters: input.filters ?? null,
            resultCount: input.resultCount ?? null,
            metadata: metadataPayload,
            statusCode: input.statusCode ?? 200,
        })

        const isSearch
            = input.eventType === 'search_fulltext'
                || input.eventType === 'search_roots'

        await db.update(userSessionActivity)
            .set({
                lastActivityAt: now,
                totalRequests: sql`${userSessionActivity.totalRequests} + 1`,
                ...(isSearch
                    ? {
                            searchRequests: sql`${userSessionActivity.searchRequests} + 1`,
                            lastSearchQuery: input.query ?? null,
                            lastFilters: input.filters ?? null,
                        }
                    : {}),
                ...(input.eventType === 'view_stats'
                    ? { statsRequests: sql`${userSessionActivity.statsRequests} + 1` }
                    : {}),
            })
            .where(eq(userSessionActivity.id, sessionActivityId))
    }
    catch (error) {
        console.warn('[Activity] Failed to log user activity:', error)
    }
}
