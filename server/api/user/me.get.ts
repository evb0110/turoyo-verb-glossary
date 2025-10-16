import { eq } from 'drizzle-orm'
import { db } from '~~/server/db'
import { user } from '~~/server/db/schema'
import { auth } from '~~/server/lib/auth'

export default defineEventHandler(async (event) => {
    try {
        const session = await auth.api.getSession({
            headers: event.headers,
        })

        if (!session?.user) {
            setResponseStatus(event, 401)
            return null
        }

        const userData = await db.select({
            id: user.id,
            name: user.name,
            email: user.email,
            image: user.image,
            role: user.role,
        }).from(user).where(eq(user.id, session.user.id)).limit(1)

        if (!userData[0]) {
            setResponseStatus(event, 404)
            return null
        }

        return userData[0]
    }
    catch (error) {
        console.error('Error fetching user:', error)
        setResponseStatus(event, 500)
        return null
    }
})
