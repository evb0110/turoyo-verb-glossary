import type { TUserRole } from '~/composables/TUserRole'

export interface IRedirectContext {
    currentPath: string
    sessionStatus: 'idle' | 'loading' | 'authenticated' | 'guest'
    userRole?: TUserRole
    isPublic: boolean
    isAdmin: boolean
}
