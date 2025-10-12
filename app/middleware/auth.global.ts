export default defineNuxtRouteMiddleware(async (to) => {
    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/blocked']

    // Server-side auth check
    if (import.meta.server) {
        const event = useRequestEvent()
        if (!event) return

        try {
            // Use event.$fetch to properly forward cookies
            const response = await event.$fetch<{ authenticated: boolean, role?: string }>('/api/auth/check')

            // Not authenticated - redirect to login (except for public routes)
            if (!response.authenticated && !publicRoutes.includes(to.path)) {
                return navigateTo('/login')
            }

            // Authenticated - check role-based access
            if (response.authenticated) {
                // Blocked users
                if (response.role === 'blocked' && to.path !== '/blocked') {
                    return navigateTo('/blocked')
                }

                // Unblocked users should not stay on blocked page
                if (response.role !== 'blocked' && to.path === '/blocked') {
                    return navigateTo('/')
                }

                // Redirect authenticated users away from login page
                if (to.path === '/login') {
                    return navigateTo('/')
                }

                // Admin-only routes
                if (to.path.startsWith('/admin') && response.role !== 'admin') {
                    return navigateTo('/')
                }
            }
        } catch (error) {
            console.error('Server auth check error:', error)
        }
        return
    }

    // Client-side auth check
    const { user, sessionStatus } = useAuth()

    // Wait for session to be loaded
    if (sessionStatus.value === 'idle' || sessionStatus.value === 'loading') {
        return
    }

    // If user is not authenticated and not on a public route, redirect to login
    if (sessionStatus.value === 'guest' && !publicRoutes.includes(to.path)) {
        return navigateTo('/login')
    }

    // If user is authenticated
    if (user.value) {
        // If blocked user, redirect to blocked page
        if (user.value.role === 'blocked' && to.path !== '/blocked') {
            return navigateTo('/blocked')
        }

        // Unblocked users should not stay on blocked page
        if (user.value.role !== 'blocked' && to.path === '/blocked') {
            return navigateTo('/')
        }

        // If user is on login page and authenticated, redirect to home
        if (to.path === '/login') {
            return navigateTo('/')
        }

        // Admin-only routes
        if (to.path.startsWith('/admin') && user.value.role !== 'admin') {
            return navigateTo('/')
        }
    }
})
