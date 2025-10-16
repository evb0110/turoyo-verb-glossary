import type { IRedirectRule } from '~/config/IRedirectRule'
import { AUTH_ROUTES } from '~/config/AUTH_ROUTES'

export const REDIRECT_RULES: IRedirectRule[] = [
    {
        name: 'blocked-user-redirect',
        priority: 100,
        condition: ctx =>
            ctx.userRole === 'blocked' && ctx.currentPath !== AUTH_ROUTES.redirectTargets.blocked,
        target: () => AUTH_ROUTES.redirectTargets.blocked,
    },
    {
        name: 'unblocked-user-on-blocked-page',
        priority: 90,
        condition: ctx =>
            !!ctx.userRole && ctx.userRole !== 'blocked' && ctx.currentPath === AUTH_ROUTES.redirectTargets.blocked,
        target: () => AUTH_ROUTES.redirectTargets.authenticated,
    },
    {
        name: 'guest-on-protected-route',
        priority: 80,
        condition: ctx =>
            ctx.sessionStatus === 'guest' && !ctx.isPublic,
        target: () => AUTH_ROUTES.redirectTargets.guest,
    },
    {
        name: 'non-admin-on-admin-route',
        priority: 70,
        condition: ctx =>
            ctx.isAdmin && ctx.userRole !== 'admin',
        target: () => AUTH_ROUTES.redirectTargets.unauthorized,
    },
    {
        name: 'authenticated-on-login-page',
        priority: 60,
        condition: ctx =>
            ctx.sessionStatus === 'authenticated' && ctx.currentPath === '/login',
        target: () => AUTH_ROUTES.redirectTargets.authenticated,
    },
]
