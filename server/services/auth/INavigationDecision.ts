export interface INavigationDecision {
    readonly shouldRedirect: boolean
    readonly redirectTo?: string
    readonly reason?: 'unauthenticated' | 'blocked' | 'unblocked' | 'already_logged_in' | 'forbidden'
}
