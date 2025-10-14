import type { RedirectContext } from '~/config/auth-routes'
import type { UserRole } from '~/composables/useAuth'
import { determineRedirect, isPublicRoute, isAdminRoute } from '~/config/auth-routes'

let isNavigating = false
let lastRedirectTime = 0
let lastRedirectTarget: string | null = null

const REDIRECT_COOLDOWN_MS = 500 // Prevent rapid successive redirects

function log(message: string, ...args: unknown[]) {
    if (import.meta.dev) {
        console.log(`[Auth Redirect] ${message}`, ...args)
    }
}

export async function safeNavigate(target: string, currentPath: string): Promise<void> {
    if (target === currentPath) {
        log('Skipped: Already on target page', { target, currentPath })
        return
    }

    const now = Date.now()
    const timeSinceLastRedirect = now - lastRedirectTime

    if (
        isNavigating
        || (target === lastRedirectTarget && timeSinceLastRedirect < REDIRECT_COOLDOWN_MS)
    ) {
        log('Skipped: Navigation in progress or cooldown active', {
            target,
            isNavigating,
            timeSinceLastRedirect,
            cooldownMs: REDIRECT_COOLDOWN_MS
        })
        return
    }

    try {
        isNavigating = true
        lastRedirectTime = now
        lastRedirectTarget = target

        log('Navigating to:', target, { from: currentPath })

        await navigateTo(target, { replace: true })
    }
    catch (error) {
        console.error('[Auth Redirect] Navigation error:', error)
    }
    finally {
        setTimeout(() => {
            isNavigating = false
        }, 100)
    }
}

export function buildRedirectContext(
    currentPath: string,
    sessionStatus: 'idle' | 'loading' | 'authenticated' | 'guest',
    userRole?: string
): RedirectContext {
    return {
        currentPath,
        sessionStatus,
        userRole: userRole as UserRole | undefined,
        isPublic: isPublicRoute(currentPath),
        isAdmin: isAdminRoute(currentPath)
    }
}

export async function handleAuthRedirect(
    currentPath: string,
    sessionStatus: 'idle' | 'loading' | 'authenticated' | 'guest',
    userRole?: string
): Promise<void> {
    const context = buildRedirectContext(currentPath, sessionStatus, userRole)

    log('Checking redirect rules', {
        path: currentPath,
        status: sessionStatus,
        role: userRole,
        isPublic: context.isPublic,
        isAdmin: context.isAdmin
    })

    const target = determineRedirect(context)

    if (target) {
        log('Redirect required', { from: currentPath, to: target })
        await safeNavigate(target, currentPath)
    }
    else {
        log('No redirect needed', { path: currentPath })
    }
}

export function resetRedirectState(): void {
    isNavigating = false
    lastRedirectTime = 0
    lastRedirectTarget = null
    log('Redirect state reset')
}
