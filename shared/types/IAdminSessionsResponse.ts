import type { IUserSessionActivity } from '#shared/types/IUserSessionActivity'

export interface IAdminSessionsResponse {
    sessions: IUserSessionActivity[]
    total: number
}
