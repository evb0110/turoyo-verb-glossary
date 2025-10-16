import type { IRedirectContext } from '~/config/IRedirectContext'

export interface IRedirectRule {
    name: string
    priority: number
    condition: (context: IRedirectContext) => boolean
    target: (context: IRedirectContext) => string
}
