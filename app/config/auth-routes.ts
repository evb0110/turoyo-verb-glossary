import type { UserRole } from '~/composables/useAuth'

export const AUTH_ROUTES = {

    public: ['/login', '/blocked'] as const,

    admin: ['/admin'] as const,

    redirectTargets: {
        guest: '/login', // Where to send unauthenticated users
        blocked: '/blocked', // Where to send blocked users
        authenticated: '/', // Where to send authenticated users (from login page)
        unauthorized: '/' // Where to send non-admin users from admin routes
    }
} as const

export function matchesRoutePattern(path: string, patterns: readonly string[]): boolean {
    return patterns.some(pattern => path === pattern || path.startsWith(`${pattern}/`))
}

export function isPublicRoute(path: string): boolean {
    return matchesRoutePattern(path, AUTH_ROUTES.public)
}

export function isAdminRoute(path: string): boolean {
    return matchesRoutePattern(path, AUTH_ROUTES.admin)
}

export interface RedirectRule {
    name: string
    priority: number
    condition: (context: RedirectContext) => boolean
    target: (context: RedirectContext) => string
}

export interface RedirectContext {
    currentPath: string
    sessionStatus: 'idle' | 'loading' | 'authenticated' | 'guest'
    userRole?: UserRole
    isPublic: boolean
    isAdmin: boolean
}

export const REDIRECT_RULES: RedirectRule[] = [
    {
        name: 'blocked-user-redirect',
        priority: 100,
        condition: ctx =>
            ctx.userRole === 'blocked' && ctx.currentPath !== AUTH_ROUTES.redirectTargets.blocked,
        target: () => AUTH_ROUTES.redirectTargets.blocked
    },
    {
        name: 'unblocked-user-on-blocked-page',
        priority: 90,
        condition: ctx =>
            !!ctx.userRole && ctx.userRole !== 'blocked' && ctx.currentPath === AUTH_ROUTES.redirectTargets.blocked,
        target: () => AUTH_ROUTES.redirectTargets.authenticated
    },
    {
        name: 'guest-on-protected-route',
        priority: 80,
        condition: ctx =>
            ctx.sessionStatus === 'guest' && !ctx.isPublic,
        target: () => AUTH_ROUTES.redirectTargets.guest
    },
    {
        name: 'non-admin-on-admin-route',
        priority: 70,
        condition: ctx =>
            ctx.isAdmin && ctx.userRole !== 'admin',
        target: () => AUTH_ROUTES.redirectTargets.unauthorized
    },
    {
        name: 'authenticated-on-login-page',
        priority: 60,
        condition: ctx =>
            ctx.sessionStatus === 'authenticated' && ctx.currentPath === '/login',
        target: () => AUTH_ROUTES.redirectTargets.authenticated
    }
]

export function determineRedirect(context: RedirectContext): string | null {
    const sortedRules = [...REDIRECT_RULES].sort((a, b) => b.priority - a.priority)

    for (const rule of sortedRules) {
        if (rule.condition(context)) {
            const target = rule.target(context)

            if (target === context.currentPath) {
                return null
            }

            return target
        }
    }

    return null
}
