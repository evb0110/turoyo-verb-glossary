import { auth } from '../../../lib/auth'
import { db } from '../../../db'
import { user } from '../../../db/schema'
import { desc, eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
    const session = await auth.api.getSession({ headers: event.headers })

    if (!session?.user) {
        throw createError({
            statusCode: 401,
            statusMessage: 'Unauthorized'
        })
    }

    const currentUser = await db.select().from(user).where(eq(user.id, session.user.id)).limit(1)

    if (!currentUser[0] || currentUser[0].role !== 'admin') {
        throw createError({
            statusCode: 403,
            statusMessage: 'Forbidden: Admin access required'
        })
    }

    const users = await db.select({
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        image: user.image,
        createdAt: user.createdAt
    }).from(user).orderBy(desc(user.createdAt))

    return users
})
