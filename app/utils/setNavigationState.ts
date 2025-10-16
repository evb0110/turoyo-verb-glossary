import type { INavigationState } from '~/utils/INavigationState'
import { state } from '~/utils/_internalNavigationState'

export function setNavigationState(newState: INavigationState): void {
    state.current = newState
}
