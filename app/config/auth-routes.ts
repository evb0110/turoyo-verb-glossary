/**
 * Centralized Auth Routes Configuration
 * Single source of truth for all auth-related routing logic
 */

import type { UserRole } from '~/composables/useAuth'

export const AUTH_ROUTES = {
    /**
   * Public routes accessible without authentication
   */
    public: ['/login', '/blocked'] as const,

    /**
   * Admin-only routes requiring admin role
   */
    admin: ['/admin'] as const,

    /**
   * Default redirect targets for various auth states
   */
    redirectTargets: {
        guest: '/login', // Where to send unauthenticated users
        blocked: '/blocked', // Where to send blocked users
        authenticated: '/', // Where to send authenticated users (from login page)
        unauthorized: '/' // Where to send non-admin users from admin routes
    }
} as const

/**
 * Check if a path matches any of the given route patterns
 */
export function matchesRoutePattern(path: string, patterns: readonly string[]): boolean {
    return patterns.some(pattern => path === pattern || path.startsWith(`${pattern}/`))
}

/**
 * Check if a path is a public route
 */
export function isPublicRoute(path: string): boolean {
    return matchesRoutePattern(path, AUTH_ROUTES.public)
}

/**
 * Check if a path is an admin route
 */
export function isAdminRoute(path: string): boolean {
    return matchesRoutePattern(path, AUTH_ROUTES.admin)
}

/**
 * Redirect rule for determining where to redirect based on auth state
 */
export interface RedirectRule {
    name: string
    priority: number
    condition: (context: RedirectContext) => boolean
    target: (context: RedirectContext) => string
}

/**
 * Context passed to redirect rules
 */
export interface RedirectContext {
    currentPath: string
    sessionStatus: 'idle' | 'loading' | 'authenticated' | 'guest'
    userRole?: UserRole
    isPublic: boolean
    isAdmin: boolean
}

/**
 * Priority-ordered redirect rules
 * Higher priority = checked first
 */
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

/**
 * Determine redirect target based on current context
 * Returns null if no redirect is needed
 */
export function determineRedirect(context: RedirectContext): string | null {
    // Sort rules by priority (highest first)
    const sortedRules = [...REDIRECT_RULES].sort((a, b) => b.priority - a.priority)

    // Find first matching rule
    for (const rule of sortedRules) {
        if (rule.condition(context)) {
            const target = rule.target(context)

            // Prevent redirect to same page (loop prevention)
            if (target === context.currentPath) {
                return null
            }

            return target
        }
    }

    return null
}
