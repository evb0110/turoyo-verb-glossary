import { AUTH_ROUTES } from '~/config/AUTH_ROUTES'
import { matchesRoutePattern } from '~/config/matchesRoutePattern'

export function isPublicRoute(path: string) {
    return matchesRoutePattern(path, AUTH_ROUTES.public)
}
