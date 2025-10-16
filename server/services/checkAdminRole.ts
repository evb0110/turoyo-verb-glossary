import type { TUserRole } from '~/composables/TUserRole'

type TUser = {
    id: string
    role: TUserRole
} | null

export function checkAdminRole<T extends TUser>(user: T) {
    if (!user) {
        return { ok: false, error: 'not_found' } as const
    }

    if (user.role !== 'admin') {
        return { ok: false, error: 'forbidden' } as const
    }

    return { ok: true as const, data: user as NonNullable<T> }
}
