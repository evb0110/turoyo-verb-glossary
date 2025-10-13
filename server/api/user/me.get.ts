import { auth } from '../../lib/auth'
import { db } from '../../db'
import { user } from '../../db/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
    try {
        const session = await auth.api.getSession({ headers: event.headers })

        if (!session?.user) {
            // Return null instead of throwing for SSR compatibility
            setResponseStatus(event, 401)
            return null
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
