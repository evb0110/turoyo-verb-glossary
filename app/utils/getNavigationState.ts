import { state } from '~/utils/_internalNavigationState'
import type { INavigationState } from '~/utils/INavigationState'

export function getNavigationState(): INavigationState {
    return {
        ...state.current,
    }
}
