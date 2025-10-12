export default defineNuxtRouteMiddleware((to) => {
    // Skip middleware on server-side and during hydration
    if (import.meta.server) return

    const { user, sessionStatus } = useAuth()

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/blocked']

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
