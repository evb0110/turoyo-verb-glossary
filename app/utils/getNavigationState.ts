import type { INavigationState } from '~/utils/INavigationState'
import { state } from '~/utils/_internalNavigationState'

export function getNavigationState(): INavigationState {
    return { ...state.current }
}
