export default defineNuxtPlugin(async () => {
    const { sessionStatus, user } = useAuth()
    const router = useRouter()

    const { handleAuthRedirect } = await import('~/utils/auth-redirect')

    if (import.meta.dev) {
        console.log('[Auth Redirect Plugin] Initialized')
    }

    watch(
        [sessionStatus, user, () => router.currentRoute.value.path],
        async ([status, currentUser, currentPath]) => {
            if (status === 'idle' || status === 'loading') {
                return
            }

            await handleAuthRedirect(
                currentPath,
                status,
                currentUser?.role
            )
        },
        {

            immediate: false
        }
    )
})
