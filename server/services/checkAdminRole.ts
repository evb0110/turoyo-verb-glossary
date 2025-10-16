import type { IUser } from '~~/server/types/IUser'

export function checkAdminRole<T extends IUser>(user: T | null) {
    if (!user) {
        return {
            ok: false,
            error: 'not_found',
        } as const
    }

    if (user.role !== 'admin') {
        return {
            ok: false,
            error: 'forbidden',
        } as const
    }

    return {
        ok: true as const,
        data: user,
    }
}
