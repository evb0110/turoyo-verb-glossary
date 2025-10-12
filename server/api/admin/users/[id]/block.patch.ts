import { auth } from '../../../../lib/auth'
import { db } from '../../../../db'
import { user } from '../../../../db/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
    // Check if user is authenticated and is admin
    const session = await auth.api.getSession({ headers: event.headers })

    if (!session?.user) {
        throw createError({
            statusCode: 401,
            statusMessage: 'Unauthorized'
        })
    }

    // Get the full user data including role
    const currentUser = await db.select().from(user).where(eq(user.id, session.user.id)).limit(1)

    if (!currentUser[0] || currentUser[0].role !== 'admin') {
        throw createError({
            statusCode: 403,
            statusMessage: 'Forbidden: Admin access required'
        })
    }

    const userId = getRouterParam(event, 'id')

    if (!userId) {
        throw createError({
            statusCode: 400,
            statusMessage: 'User ID is required'
        })
    }

    // Prevent admin from blocking themselves
    if (userId === session.user.id) {
        throw createError({
            statusCode: 400,
            statusMessage: 'Cannot block yourself'
        })
    }

    // Update user role to 'blocked'
    const updated = await db.update(user)
        .set({ role: 'blocked' })
        .where(eq(user.id, userId))
        .returning()

    if (!updated[0]) {
        throw createError({
            statusCode: 404,
            statusMessage: 'User not found'
        })
    }

    return { success: true, user: updated[0] }
})
