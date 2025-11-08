import type { TUserRole } from '#shared/types/TUserRole'

export interface IUserSessionActivity {
    id: string
    sessionId: string
    userId: string
    userName: string | null
    userEmail: string | null
    userRole: TUserRole
    ipAddress: string | null
    userAgent: string | null
    createdAt: string | Date
    lastActivityAt: string | Date
    totalRequests: number
    searchRequests: number
    statsRequests: number
    lastSearchQuery: string | null
    lastFilters: Record<string, unknown> | null
}
