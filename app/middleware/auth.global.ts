import { authorizeNavigation } from '~~/server/services/auth/authorizeNavigation'
import type { IAuthUser } from '#shared/types/IAuthUser'

export default defineNuxtRouteMiddleware(async (to) => {
    if (import.meta.server) {
        const event = useRequestEvent()
        if (!event) return

        try {
            const userData = await $fetch<IAuthUser | null>('/api/user/me', { headers: event.headers }).catch(() => null)

            useState('auth:user').value = userData
            useState('auth:sessionStatus').value = userData ? 'authenticated' : 'guest'

            const {
                shouldRedirect,
                redirectTo,
            } = authorizeNavigation(userData, to.path)
            if (shouldRedirect && redirectTo) {
                return navigateTo(redirectTo)
            }
        }
        catch (error) {
            console.error('Server auth check error:', error)
        }
        return
    }

    const {
        user,
        sessionStatus,
    } = useAuth()

    if (sessionStatus.value === 'idle' || sessionStatus.value === 'loading') {
        return
    }

    const {
        shouldRedirect,
        redirectTo,
    } = authorizeNavigation(user.value, to.path)
    if (shouldRedirect && redirectTo) {
        return navigateTo(redirectTo)
    }
})
