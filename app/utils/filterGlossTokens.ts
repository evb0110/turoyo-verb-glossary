import type { IGlossToken } from '~/types/IGlossToken'

export function filterGlossTokens(tokens: IGlossToken[]): IGlossToken[] {
    if (!Array.isArray(tokens)) return []

    return tokens.filter((t, idx, arr) => {
        const first = arr[0]?.text?.trim() || ''

        if (idx === 0 && /^[IVX]+\s*:/.test(first)) return false
        return true
    })
}
