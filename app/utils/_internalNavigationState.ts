import type { INavigationState } from '~/utils/INavigationState'

export const state: { current: INavigationState } = {
    current: {
        isNavigating: false,
        lastRedirectTime: 0,
        lastRedirectTarget: null
    }
}
