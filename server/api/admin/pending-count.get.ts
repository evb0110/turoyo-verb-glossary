import { eq, count } from 'drizzle-orm'
import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { requireApproved } from '~~/server/services/auth/requireApproved'
import type { IPendingCountResponse } from '~~/server/types/IPendingCountResponse'

export default defineEventHandler<Promise<IPendingCountResponse>>(async (event) => {
    const currentUser = await requireApproved(event)
    if (currentUser.role !== 'admin') throw createError({
        statusCode: 403,
        message: 'Admin access required.',
    })

    const result = await db.select({ count: count() }).from(user).where(eq(user.role, 'pending'))

    return { count: result[0]?.count || 0 }
})
