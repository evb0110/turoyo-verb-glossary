import type { INavigationState } from '~/types/INavigationState'
import { state } from '~/utils/_internalNavigationState'

export function getNavigationState(): INavigationState {
    return { ...state.current }
}
