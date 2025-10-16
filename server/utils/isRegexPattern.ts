export function isRegexPattern(pattern: string) {
    if (/\\[cv]/i.test(pattern)) {
        return true
    }

    const regexMetaChars = /[.*+?^${}()|[\]]/
    return regexMetaChars.test(pattern)
}
