import type { TUserRole } from '~/composables/TUserRole'

export interface IAuthUser {
    id: string
    name: string
    email: string
    image?: string | null
    role: TUserRole
    createdAt: string
}
