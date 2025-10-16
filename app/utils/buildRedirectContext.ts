import type { IRedirectContext } from '~/config/IRedirectContext'
import { isAdminRoute } from '~/config/isAdminRoute'
import { isPublicRoute } from '~/config/isPublicRoute'
import type { TUserRole } from '~/types/TUserRole'

export function buildRedirectContext(
    currentPath: string,
    sessionStatus: 'idle' | 'loading' | 'authenticated' | 'guest',
    userRole?: string
): IRedirectContext {
    return {
        currentPath,
        sessionStatus,
        userRole: userRole as TUserRole | undefined,
        isPublic: isPublicRoute(currentPath),
        isAdmin: isAdminRoute(currentPath),
    }
}
