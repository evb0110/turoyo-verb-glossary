import type { IRedirectContext } from '~/config/IRedirectContext'
import { REDIRECT_RULES } from '~/config/REDIRECT_RULES'

export function determineRedirect(context: IRedirectContext): string | null {
    const sortedRules = [...REDIRECT_RULES].sort((a, b) => b.priority - a.priority)

    for (const rule of sortedRules) {
        if (rule.condition(context)) {
            const target = rule.target(context)

            if (target === context.currentPath) {
                return null
            }

            return target
        }
    }

    return null
}
