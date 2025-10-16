import type { IRedirectContext } from '~/config/IRedirectContext'
import type { TUserRole } from '~/composables/TUserRole'
import { isPublicRoute } from '~/config/isPublicRoute'
import { isAdminRoute } from '~/config/isAdminRoute'

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
        isAdmin: isAdminRoute(currentPath)
    }
}
