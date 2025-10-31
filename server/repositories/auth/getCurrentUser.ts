import { getAuth } from '~~/server/lib/auth'
import { getUserById } from '~~/server/repositories/auth/getUserById'
import type { H3Event } from 'h3'

export async function getCurrentUser(event: H3Event) {
    const auth = getAuth(event)
    const session = await auth.api.getSession({ headers: event.headers })

    if (!session?.user) {
        return null
    }

    return getUserById(session.user.id, event)
}
