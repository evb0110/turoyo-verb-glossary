import { authorizeNavigation } from '~~/server/services/auth/authorizeNavigation'
import type { IAuthUser } from '#shared/types/IAuthUser'

export default defineNuxtRouteMiddleware(async (to) => {
    if (import.meta.server) {
        const event = useRequestEvent()
        if (!event) return

        try {
            const userData = await $fetch<IAuthUser | null>('/api/user/me', { headers: { cookie: event.headers.get('cookie') || '' } })

            useState('auth:user').value = userData
            useState('auth:sessionStatus').value = userData ? 'authenticated' : 'guest'
            if (userData?.role === 'pending' && to.path !== '/') return navigateTo('/')

            const {
                shouldRedirect,
                redirectTo,
            } = authorizeNavigation(userData, to.path)
            if (shouldRedirect && redirectTo) {
                return navigateTo(redirectTo)
            }
        }
        catch (error) {
            if ((error as { statusCode?: number }).statusCode !== 401) {
                console.error('Server auth check error:', error)
            }
            useState('auth:user').value = null
            useState('auth:sessionStatus').value = 'guest'
            const decision = authorizeNavigation(null, to.path)
            if (decision.shouldRedirect && decision.redirectTo) return navigateTo(decision.redirectTo)
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

    if (user.value?.role === 'pending' && to.path !== '/') return navigateTo('/')

    const {
        shouldRedirect,
        redirectTo,
    } = authorizeNavigation(user.value, to.path)
    if (shouldRedirect && redirectTo) {
        return navigateTo(redirectTo)
    }
})
