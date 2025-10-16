import { setNavigationState } from '~/utils/setNavigationState'

export function resetRedirectState(): void {
    setNavigationState({
        isNavigating: false,
        lastRedirectTime: 0,
        lastRedirectTarget: null,
    })
}
