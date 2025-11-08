import type { TActivityEventType } from '#shared/config/activityEventTypes'
import type { IUserActivityLog } from '#shared/types/IUserActivityLog'

export interface IAdminActivityResponse {
    events: IUserActivityLog[]
    total: number
    counts: Record<TActivityEventType, number>
}
