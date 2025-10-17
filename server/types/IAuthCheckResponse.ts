import type { TUserRole } from '~~/types/TUserRole'

export interface IAuthCheckResponse {
    authenticated: boolean
    role?: TUserRole
}
