import type { INavigationDecision } from '~/types/INavigationDecision'
import type { INavigationState } from '~/types/INavigationState'

const REDIRECT_COOLDOWN_MS = 500

export function canNavigate(
    target: string,
    currentPath: string,
    now: number,
    state: INavigationState
): INavigationDecision {
    if (target === currentPath) {
        return {
            shouldNavigate: false,
            reason: 'Already on target page',
            newState: state,
        }
    }

    const timeSinceLastRedirect = now - state.lastRedirectTime

    if (state.isNavigating) {
        return {
            shouldNavigate: false,
            reason: 'Navigation in progress',
            newState: state,
        }
    }

    if (target === state.lastRedirectTarget && timeSinceLastRedirect < REDIRECT_COOLDOWN_MS) {
        return {
            shouldNavigate: false,
            reason: `Cooldown active (${timeSinceLastRedirect}ms < ${REDIRECT_COOLDOWN_MS}ms)`,
            newState: state,
        }
    }

    return {
        shouldNavigate: true,
        newState: {
            isNavigating: true,
            lastRedirectTime: now,
            lastRedirectTarget: target,
        },
    }
}
