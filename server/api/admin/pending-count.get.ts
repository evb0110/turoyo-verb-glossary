import { eq, count } from 'drizzle-orm'
import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { auth } from '~~/server/lib/auth'

export default defineEventHandler(async (event) => {
    const session = await auth.api.getSession({
        headers: event.headers,
    })

    if (!session?.user) {
        throw createError({
            statusCode: 401,
            statusMessage: 'Unauthorized',
        })
    }

    const currentUser = await db.select().from(user).where(eq(user.id, session.user.id)).limit(1)

    if (!currentUser[0] || currentUser[0].role !== 'admin') {
        throw createError({
            statusCode: 403,
            statusMessage: 'Forbidden: Admin access required',
        })
    }

    const result = await db.select({
        count: count(),
    }).from(user).where(eq(user.role, 'pending'))

    return {
        count: result[0]?.count || 0,
    }
})
