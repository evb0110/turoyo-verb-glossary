import type { IAuthUser } from '#shared/types/IAuthUser'

export interface IUserActionResponse {
    success: boolean
    user: IAuthUser
}
