import type { IAuthUser } from '~~/types/IAuthUser'

export interface IUserActionResponse {
    success: boolean
    user: IAuthUser
}
