import { matchesRoutePattern } from '~/config/matchesRoutePattern'
import { AUTH_ROUTES } from '~/config/AUTH_ROUTES'

export function isAdminRoute(path: string) {
    return matchesRoutePattern(path, AUTH_ROUTES.admin)
}
