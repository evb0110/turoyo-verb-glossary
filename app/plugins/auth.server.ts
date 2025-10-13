interface AuthUser {
    id: string
    name: string
    email: string
    image?: string | null
    role: string
}

export default defineNuxtPlugin(async (_nuxtApp) => {
    // Only run on server
    if (import.meta.client) return

    const event = useRequestEvent()
    if (!event) return

    try {
        // Fetch user data with role during SSR
        const userData = await $fetch<AuthUser | null>('/api/user/me', {
            headers: event.headers as HeadersInit
        }).catch(() => null)

        console.log('[auth.server.ts] User data fetched:', userData)

        if (userData) {
            // Set initial auth state that will be hydrated on client
            const authState = useState<AuthUser | null>('auth:user', () => null)
            const sessionStatus = useState<string>('auth:sessionStatus', () => 'idle')

            authState.value = userData
            sessionStatus.value = 'authenticated'

            console.log('[auth.server.ts] State set:', { user: authState.value, status: sessionStatus.value })
        }
    }
    catch (error) {
        console.error('Server auth initialization error:', error)
    }
})
