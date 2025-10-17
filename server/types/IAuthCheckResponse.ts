import type { TUserRole } from '#shared/types/TUserRole'

export interface IAuthCheckResponse {
    authenticated: boolean
    role?: TUserRole
}
