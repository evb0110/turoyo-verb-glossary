import { expandRegexShortcuts } from '~~/server/utils/expandRegexShortcuts'

export function createSearchRegex(
    pattern: string,
    options: {
        caseSensitive?: boolean
    } = {}
): RegExp | null {
    const { caseSensitive = false } = options

    const expandedPattern = expandRegexShortcuts(pattern)

    const flags = `${caseSensitive ? '' : 'i'}u`

    try {
        return new RegExp(expandedPattern, flags)
    }
    catch {
        return null
    }
}
