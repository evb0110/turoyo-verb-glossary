import type { TAuthError } from '~~/server/services/TAuthError'

export type IAuthResult<T>
    = { ok: true, data: T }
        | { ok: false, error: TAuthError }
