import type { TActivityEventType } from '#shared/config/activityEventTypes'
import type { TUserRole } from '#shared/types/TUserRole'

export interface IUserActivityLog {
    id: string
    host: string | null
    userId: string
    userName: string | null
    userEmail: string | null
    userRole: TUserRole
    sessionActivityId: string | null
    sessionId: string | null
    eventType: TActivityEventType
    path: string | null
    query: string | null
    filters: Record<string, unknown> | null
    resultCount: number | null
    metadata: Record<string, unknown> | null
    statusCode: number
    createdAt: string | Date
}
