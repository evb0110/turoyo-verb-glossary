import type { INavigationDecision } from '~~/server/services/auth/INavigationDecision'
import type { IAuthUser } from '#shared/types/IAuthUser'

const PUBLIC_ROUTES = ['/login', '/blocked']

export function authorizeNavigation(
    user: IAuthUser | null,
    targetPath: string
): INavigationDecision {
    if (!user && !PUBLIC_ROUTES.includes(targetPath)) {
        return {
            shouldRedirect: true,
            redirectTo: '/login',
            reason: 'unauthenticated',
        }
    }

    if (user) {
        if (user.role === 'blocked' && targetPath !== '/blocked') {
            return {
                shouldRedirect: true,
                redirectTo: '/blocked',
                reason: 'blocked',
            }
        }

        if (user.role !== 'blocked' && targetPath === '/blocked') {
            return {
                shouldRedirect: true,
                redirectTo: '/',
                reason: 'unblocked',
            }
        }

        if (targetPath === '/login') {
            return {
                shouldRedirect: true,
                redirectTo: '/',
                reason: 'already_logged_in',
            }
        }

        if (targetPath.startsWith('/admin') && user.role !== 'admin') {
            return {
                shouldRedirect: true,
                redirectTo: '/',
                reason: 'forbidden',
            }
        }
    }

    return { shouldRedirect: false }
}
