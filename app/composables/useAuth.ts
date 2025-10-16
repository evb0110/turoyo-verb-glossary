import { createAuthClient } from 'better-auth/vue'
import type { IAuthUser } from '~/composables/IAuthUser'

let authClient: ReturnType<typeof createAuthClient> | null = null

function getAuthClient() {
    if (authClient) return authClient

    const baseURL = typeof window !== 'undefined'
        ? window.location.origin
        : useRuntimeConfig().public.siteUrl

    authClient = createAuthClient({
        baseURL,
    })
    return authClient
}

export const useAuth = () => {
    const client = getAuthClient()
    const user = useState<IAuthUser | null>('auth:user', () => null)
    const loading = useState<boolean>('auth:loading', () => false)
    const sessionStatus = useState<'idle' | 'loading' | 'authenticated' | 'guest'>('auth:sessionStatus', () => 'idle')

    const isSessionKnown = computed(() =>
        sessionStatus.value === 'authenticated' || sessionStatus.value === 'guest'
    )

    const isAdmin = computed(() => user.value?.role === 'admin')
    const isPending = computed(() => user.value?.role === 'pending')
    const isBlocked = computed(() => user.value?.role === 'blocked')
    const isApproved = computed(() => user.value?.role === 'user' || user.value?.role === 'admin')

    const pendingKey = 'turoyo-verb-glossary:auth-returning'

    const signIn = async () => {
        loading.value = true
        try {
            if (typeof window !== 'undefined') {
                window.sessionStorage.setItem(pendingKey, '1')
            }
            sessionStatus.value = 'loading'
            await client.signIn.social({
                provider: 'google',
                callbackURL: '/',
            })
        }
        catch (error) {
            console.error('Sign in error:', error)
            if (typeof window !== 'undefined') {
                window.sessionStorage.removeItem(pendingKey)
            }
        }
        finally {
            loading.value = false
        }
    }

    const checkSession = async () => {
        if (sessionStatus.value === 'authenticated' && user.value) {
            return
        }

        sessionStatus.value = 'loading'

        try {
            const session = await client.getSession()

            if (session.data?.user) {
                const response = await $fetch<IAuthUser | null>('/api/user/me')
                if (response) {
                    user.value = response
                    sessionStatus.value = 'authenticated'
                }
                else {
                    user.value = null
                    sessionStatus.value = 'guest'
                }
            }
            else {
                user.value = null
                sessionStatus.value = 'guest'
            }
        }
        catch (error) {
            console.error('Session check error:', error)
            user.value = null
            sessionStatus.value = 'guest'
        }
        finally {
            if (typeof window !== 'undefined') {
                window.sessionStorage.removeItem(pendingKey)
            }
        }
    }

    const signOut = async () => {
        try {
            await client.signOut()
            user.value = null
            sessionStatus.value = 'guest'
            if (typeof window !== 'undefined') {
                window.sessionStorage.removeItem(pendingKey)
            }
        }
        catch (error) {
            console.error('Sign out error:', error)
        }
    }

    return {
        user,
        loading,
        sessionStatus,
        isSessionKnown,
        isAdmin,
        isPending,
        isBlocked,
        isApproved,
        signIn,
        signOut,
        checkSession,
    }
}
