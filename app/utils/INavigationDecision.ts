import type { INavigationState } from '~/utils/INavigationState'

export interface INavigationDecision {
    shouldNavigate: boolean
    reason?: string
    newState: INavigationState
}
