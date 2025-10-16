import { auth } from '~~/server/lib/auth'
import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
    try {
        const session = await auth.api.getSession({ headers: event.headers })

        if (!session?.user) {
            return { authenticated: false }
        }

        const userData = await db.select().from(user).where(eq(user.id, session.user.id)).limit(1)
        const currentUser = userData[0]

        if (!currentUser) {
            return { authenticated: false }
        }

        return {
            authenticated: true,
            role: currentUser.role,
        }
    }
    catch (error) {
        console.error('Auth check error:', error)
        return { authenticated: false }
    }
})
