import { createAuthClient } from 'better-auth/vue'
import type { BetterAuthClient } from 'better-auth/vue'

let authClient: BetterAuthClient | null = null

function getAuthClient() {
    if (authClient) return authClient

    const baseURL = typeof window !== 'undefined'
        ? window.location.origin
        : useRuntimeConfig().public.siteUrl

    authClient = createAuthClient({ baseURL })
    return authClient
}

export type UserRole = 'admin' | 'user' | 'pending' | 'blocked'

export interface AuthUser {
    id: string
    name: string
    email: string
    image?: string | null
    role: UserRole
}

export const useAuth = () => {
    const client = getAuthClient()
    const user = useState<AuthUser | null>('auth:user', () => null)
    const loading = useState<boolean>('auth:loading', () => false)
    const sessionStatus = useState<'idle' | 'loading' | 'authenticated' | 'guest'>('auth:sessionStatus', () => 'idle')

    // Helper computed for UI states
    const isSessionKnown = computed(() =>
        sessionStatus.value === 'authenticated' || sessionStatus.value === 'guest'
    )

    // Role-based computed helpers
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
                callbackURL: '/'
            })
        } catch (error) {
            console.error('Sign in error:', error)
            if (typeof window !== 'undefined') {
                window.sessionStorage.removeItem(pendingKey)
            }
        } finally {
            loading.value = false
        }
    }

    const checkSession = async () => {
        sessionStatus.value = 'loading'

        try {
            const session = await client.getSession()
            console.log('Session:', session)

            if (session.data?.user) {
                // Fetch full user data including role from our API
                const response = await $fetch<AuthUser>('/api/user/me')
                user.value = response
                sessionStatus.value = 'authenticated'
            } else {
                user.value = null
                sessionStatus.value = 'guest'
            }
        } catch (error) {
            console.error('Session check error:', error)
            user.value = null
            sessionStatus.value = 'guest'
        } finally {
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
        } catch (error) {
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
        checkSession
    }
}
