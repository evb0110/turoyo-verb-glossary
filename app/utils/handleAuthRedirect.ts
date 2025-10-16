import { determineRedirect } from '~/config/determineRedirect'
import { buildRedirectContext } from '~/utils/buildRedirectContext'
import { safeNavigate } from '~/utils/safeNavigate'

function log(message: string, ...args: unknown[]) {
    if (import.meta.dev) {
        console.log(`[Auth Redirect] ${message}`, ...args)
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
