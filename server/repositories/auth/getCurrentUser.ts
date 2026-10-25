import { getAuth } from '~~/server/lib/auth'
import { getUserById } from '~~/server/repositories/auth/getUserById'
import type { IAuthUser } from '#shared/types/IAuthUser'
import type { H3Event } from 'h3'

export async function getCurrentUser(event: H3Event): Promise<IAuthUser | null> {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') {
        const role = process.env.NUXT_DEV_AUTH_ROLE || 'user'
        if (role === 'guest') return null
        return {
            id: 'dev-reviewer',
            name: 'Development reviewer',
            email: 'reviewer@example.invalid',
            role: role === 'pending' || role === 'blocked' || role === 'admin' ? role : 'user',
            createdAt: '2026-10-25T00:00:00Z',
        }
    }
    if (event.context.glossaryUser !== undefined) return event.context.glossaryUser
    const auth = getAuth(event)
    const session = await auth.api.getSession({ headers: event.headers })
    const user = session?.user ? await getUserById(session.user.id, event) : null
    event.context.glossaryUser = user
    return user
}
