const TUROYO_VOWELS = '(?:a|e|i|o|u|ə|ǝ|é|ī|á|í|ó|ú|ā|ē|ō|ū)'

const TUROYO_CONSONANTS = '(?:b|d|f|g|h|k|l|m|n|p|q|r|s|t|v|w|x|y|z|č|ġ|š|ž|ǧ|ʔ|ʕ|ḏ|ḥ|ḷ|ṣ|ṭ|ṯ|ḅ|ḍ|ḳ|ẓ)'

export function expandRegexShortcuts(pattern: string): string {
    return pattern
        .replace(/\\v/gi, TUROYO_VOWELS)
        .replace(/\\c/gi, TUROYO_CONSONANTS)
}

export function isRegexPattern(pattern: string): boolean {
    if (/\\[cv]/i.test(pattern)) {
        return true
    }

    const regexMetaChars = /[.*+?^${}()|[\]]/
    return regexMetaChars.test(pattern)
}

export function createSearchRegex(
    pattern: string,
    options: {
        caseSensitive?: boolean
    } = {}
): RegExp | null {
    const { caseSensitive = false } = options

    const expandedPattern = expandRegexShortcuts(pattern)

    const flags = `${caseSensitive ? '' : 'i'}u` // always use unicode flag

    try {
        return new RegExp(expandedPattern, flags)
    }
    catch {
        return null
    }
}

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

export function makeGlobalRegex(regex: RegExp): RegExp {
    const flags = regex.flags.includes('g') ? regex.flags : `g${regex.flags}`
    return new RegExp(regex.source, flags)
}

export function* matchAll(text: string, regex: RegExp): Generator<RegExpExecArray> {
    const globalRegex = makeGlobalRegex(regex)
    let match: RegExpExecArray | null

    while ((match = globalRegex.exec(text)) !== null) {
        yield match

        if (match[0].length === 0) {
            globalRegex.lastIndex += 1
        }
    }
}
