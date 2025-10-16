import type { INavigationState } from '~/utils/INavigationState'
import { state } from '~/utils/_internalNavigationState'

export function updateNavigationState(updates: Partial<INavigationState>): void {
    state.current = {
        ...state.current,
        ...updates,
    }
}
