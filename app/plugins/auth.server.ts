import type { IAuthUser } from '~/types/IAuthUser'

export default defineNuxtPlugin(async (_nuxtApp) => {
    if (import.meta.client) return

    const event = useRequestEvent()
    if (!event) return

    try {
        const userData = await $fetch<IAuthUser | null>('/api/user/me', {
            headers: event.headers as HeadersInit,
        }).catch(() => null)

        console.log('[auth.server.ts] User data fetched:', userData)

        if (userData) {
            const authState = useState('auth:user', () => null as IAuthUser | null)
            const sessionStatus = useState('auth:sessionStatus', () => 'idle')

            authState.value = userData
            sessionStatus.value = 'authenticated'

            console.log('[auth.server.ts] State set:', {
                user: authState.value,
                status: sessionStatus.value,
            })
        }
        else {
            const authState = useState('auth:user', () => null as IAuthUser | null)
            const sessionStatus = useState('auth:sessionStatus', () => 'idle')

            authState.value = null
            sessionStatus.value = 'guest'
        }
    }
    catch (error) {
        console.error('Server auth initialization error:', error)
    }
})
