import { canNavigate } from '~/utils/canNavigate'
import { getNavigationState } from '~/utils/getNavigationState'
import { setNavigationState } from '~/utils/setNavigationState'
import { updateNavigationState } from '~/utils/updateNavigationState'

export async function safeNavigate(
    target: string,
    currentPath: string,
    now: number = Date.now()
): Promise<void> {
    const navigationState = getNavigationState()
    const decision = canNavigate(target, currentPath, now, navigationState)

    if (!decision.shouldNavigate) {
        return
    }

    setNavigationState(decision.newState)

    try {
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
