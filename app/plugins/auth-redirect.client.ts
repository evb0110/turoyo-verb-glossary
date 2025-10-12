/**
 * Global Auth Redirect Plugin
 *
 * Centralized client-side authentication redirect logic.
 * Watches auth state changes and handles redirects automatically.
 *
 * Architecture:
 * - Middleware (auth.global.ts): Handles SSR + route navigation redirects
 * - This Plugin: Handles client-side auth state change redirects
 *
 * This prevents the bug where logging out from admin page leaves you on a
 * non-functional page because the component doesn't re-run its setup code.
 */

export default defineNuxtPlugin(async () => {
  const { sessionStatus, user } = useAuth()
  const router = useRouter()

  // Import redirect utilities
  const { handleAuthRedirect } = await import('~/utils/auth-redirect')

  if (import.meta.dev) {
    console.log('[Auth Redirect Plugin] Initialized')
  }

  /**
   * Watch for auth state changes and trigger redirects
   *
   * This watcher handles:
   * 1. User logs out → redirect to /login
   * 2. User gets blocked → redirect to /blocked
   * 3. User gets unblocked while on /blocked → redirect to /
   * 4. User loses admin role while on /admin → redirect to /
   * 5. User gains authentication while on /login → redirect to /
   */
  watch(
    [sessionStatus, user, () => router.currentRoute.value.path],
    async ([status, currentUser, currentPath]) => {
      // Skip if session is still loading
      if (status === 'idle' || status === 'loading') {
        return
      }

      // Handle redirect logic
      await handleAuthRedirect(
        currentPath,
        status,
        currentUser?.role
      )
    },
    {
      // Don't run immediately on mount - let middleware handle initial navigation
      immediate: false,
    }
  )
})
