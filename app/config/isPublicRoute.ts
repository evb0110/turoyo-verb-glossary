import { matchesRoutePattern } from '~/config/matchesRoutePattern'
import { AUTH_ROUTES } from '~/config/AUTH_ROUTES'

export function isPublicRoute(path: string): boolean {
    return matchesRoutePattern(path, AUTH_ROUTES.public)
}
