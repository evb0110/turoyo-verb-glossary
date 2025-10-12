import { auth } from '../../lib/auth'
import { db } from '../../db'
import { user } from '../../db/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
    const session = await auth.api.getSession({ headers: event.headers })

    if (!session?.user) {
        throw createError({
            statusCode: 401,
            statusMessage: 'Unauthorized'
        })
    }

    // Get the full user data including role
    const userData = await db.select({
        id: user.id,
        name: user.name,
        email: user.email,
        image: user.image,
        role: user.role
    }).from(user).where(eq(user.id, session.user.id)).limit(1)

    if (!userData[0]) {
        throw createError({
            statusCode: 404,
            statusMessage: 'User not found'
        })
    }

    return userData[0]
})
