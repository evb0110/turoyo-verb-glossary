type User = {
    id: string
    role: 'admin' | 'user' | 'pending' | 'blocked'
} | null

export function checkAdminRole<T extends User>(user: T) {
    if (!user) {
        return { ok: false as const, error: 'not_found' as const }
    }

    if (user.role !== 'admin') {
        return { ok: false as const, error: 'forbidden' as const }
    }

    return { ok: true as const, data: user as NonNullable<T> }
}
