import { state } from '~/utils/_internalNavigationState'
import type { INavigationState } from '~/utils/INavigationState'

export function updateNavigationState(updates: Partial<INavigationState>): void {
    state.current = {
        ...state.current,
        ...updates,
    }
}
