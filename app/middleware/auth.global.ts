export default defineNuxtRouteMiddleware(async (to) => {
    const publicRoutes = ['/login', '/blocked']

    if (import.meta.server) {
        const event = useRequestEvent()
        if (!event) return

        try {
            const response = await event.$fetch<{ authenticated: boolean
                role?: string }>('/api/auth/check')

            if (!response.authenticated && !publicRoutes.includes(to.path)) {
                return navigateTo('/login')
            }

            if (response.authenticated) {
                if (response.role === 'blocked' && to.path !== '/blocked') {
                    return navigateTo('/blocked')
                }

                if (response.role !== 'blocked' && to.path === '/blocked') {
                    return navigateTo('/')
                }

                if (to.path === '/login') {
                    return navigateTo('/')
                }

                if (to.path.startsWith('/admin') && response.role !== 'admin') {
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
