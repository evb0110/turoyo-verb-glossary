import type { INavigationState } from '~/types/INavigationState'

export interface INavigationDecision {
    shouldNavigate: boolean
    reason?: string
    newState: INavigationState
}
