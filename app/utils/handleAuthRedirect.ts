import { determineRedirect } from '~/config/determineRedirect'
import { buildRedirectContext } from '~/utils/buildRedirectContext'
import { safeNavigate } from '~/utils/safeNavigate'

export async function handleAuthRedirect(
    currentPath: string,
    sessionStatus: 'idle' | 'loading' | 'authenticated' | 'guest',
    userRole?: string
): Promise<void> {
    const context = buildRedirectContext(currentPath, sessionStatus, userRole)
    const target = determineRedirect(context)

    if (target) {
        await safeNavigate(target, currentPath)
    }
}
