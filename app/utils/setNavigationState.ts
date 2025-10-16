import type { INavigationState } from '~/types/INavigationState'
import { state } from '~/utils/_internalNavigationState'

export function setNavigationState(newState: INavigationState): void {
    state.current = newState
}
