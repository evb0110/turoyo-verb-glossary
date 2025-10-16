import { createSearchRegex } from '~~/server/utils/createSearchRegex'

export function matchesPattern(
    text: string,
    pattern: string,
    options: {
        caseSensitive?: boolean
        useRegex?: boolean
    } = {}
): boolean {
    const { caseSensitive = false, useRegex = false } = options

    if (!pattern) {
        return false
    }

    if (!useRegex) {
        return caseSensitive
            ? text.includes(pattern)
            : text.toLowerCase().includes(pattern.toLowerCase())
    }

    const regex = createSearchRegex(pattern, { caseSensitive })
    if (!regex) {
        return caseSensitive
            ? text.includes(pattern)
            : text.toLowerCase().includes(pattern.toLowerCase())
    }

    return regex.test(text)
}
