import type { IAuthResult } from '~~/server/services/IAuthResult'

type User = {
    id: string
    role: 'admin' | 'user' | 'pending' | 'blocked'
} | null

export function checkAdminRole<T extends User>(user: T): IAuthResult<NonNullable<T>> {
    if (!user) {
        return { ok: false, error: 'not_found' }
    }

    if (user.role !== 'admin') {
        return { ok: false, error: 'forbidden' }
    }

    return { ok: true, data: user }
}
