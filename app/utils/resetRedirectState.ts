import { setNavigationState } from '~/utils/setNavigationState'

function log(message: string, ...args: unknown[]) {
    if (import.meta.dev) {
        console.log(`[Auth Redirect] ${message}`, ...args)
    }
}

export function resetRedirectState(): void {
    setNavigationState({
        isNavigating: false,
        lastRedirectTime: 0,
        lastRedirectTarget: null
    })
    log('Redirect state reset')
}
