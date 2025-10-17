import type { IAuthUser } from '#shared/types/IAuthUser'

export default defineNuxtRouteMiddleware(async (to) => {
    const publicRoutes = ['/login', '/blocked']

    if (import.meta.server) {
        const event = useRequestEvent()
        if (!event) return

        try {
            const userData = await $fetch<IAuthUser | null>('/api/user/me', { headers: event.headers as HeadersInit }).catch(() => null)

            useState('auth:user').value = userData
            useState('auth:sessionStatus').value = userData ? 'authenticated' : 'guest'

            if (!userData && !publicRoutes.includes(to.path)) {
                return navigateTo('/login')
            }

            if (userData) {
                if (userData.role === 'blocked' && to.path !== '/blocked') {
                    return navigateTo('/blocked')
                }

                if (userData.role !== 'blocked' && to.path === '/blocked') {
                    return navigateTo('/')
                }

                if (to.path === '/login') {
                    return navigateTo('/')
                }

                if (to.path.startsWith('/admin') && userData.role !== 'admin') {
                    return navigateTo('/')
                }
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

    if (sessionStatus.value === 'guest' && !publicRoutes.includes(to.path)) {
        return navigateTo('/login')
    }

    if (user.value) {
        if (user.value.role === 'blocked' && to.path !== '/blocked') {
            return navigateTo('/blocked')
        }

        if (user.value.role !== 'blocked' && to.path === '/blocked') {
            return navigateTo('/')
        }

        if (to.path === '/login') {
            return navigateTo('/')
        }

        if (to.path.startsWith('/admin') && user.value.role !== 'admin') {
            return navigateTo('/')
        }
    }
})
