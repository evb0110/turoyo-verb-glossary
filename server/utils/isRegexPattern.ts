export function isRegexPattern(pattern: string): boolean {
    if (/\\[cv]/i.test(pattern)) {
        return true
    }

    const regexMetaChars = /[.*+?^${}()|[\]]/
    return regexMetaChars.test(pattern)
}
