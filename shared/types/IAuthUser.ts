import type { TUserRole } from '#shared/types/TUserRole'

export interface IAuthUser {
    id: string
    name: string
    email: string
    image?: string | null
    role: TUserRole
    createdAt: Date | string
}
