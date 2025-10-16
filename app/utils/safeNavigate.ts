import { canNavigate } from '~/utils/canNavigate'
import { getNavigationState } from '~/utils/getNavigationState'
import { setNavigationState } from '~/utils/setNavigationState'
import { updateNavigationState } from '~/utils/updateNavigationState'

function log(message: string, ...args: unknown[]) {
    if (import.meta.dev) {
        console.log(`[Auth Redirect] ${message}`, ...args)
    }
}

export async function safeNavigate(
    target: string,
    currentPath: string,
    now: number = Date.now()
): Promise<void> {
    const navigationState = getNavigationState()
    const decision = canNavigate(target, currentPath, now, navigationState)

    if (!decision.shouldNavigate) {
        log(`Skipped: ${decision.reason}`, {
            target,
            currentPath,
        })
        return
    }

    setNavigationState(decision.newState)

    try {
        log('Navigating to:', target, {
            from: currentPath,
        })
        await navigateTo(target, {
            replace: true,
        })
    }
    catch (error) {
        console.error('[Auth Redirect] Navigation error:', error)
    }
    finally {
        setTimeout(() => {
            updateNavigationState({
                isNavigating: false,
            })
        }, 100)
    }
}
