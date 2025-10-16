import { state } from '~/utils/_internalNavigationState'
import type { INavigationState } from '~/utils/INavigationState'

export function setNavigationState(newState: INavigationState): void {
    state.current = newState
}
