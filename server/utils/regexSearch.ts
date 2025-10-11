/**
 * Server-side regex search utilities for Turoyo text
 * Supports custom shortcuts: \c for consonants, \v for vowels
 */

// Turoyo vowels pattern
const TUROYO_VOWELS = '(?:a|e|i|o|u|ə|ǝ|é|ī|á|í|ó|ú|ā|ē|ō|ū)'

// Turoyo consonants pattern
const TUROYO_CONSONANTS = '(?:b|d|f|g|h|k|l|m|n|p|q|r|s|t|v|w|x|y|z|č|ġ|š|ž|ǧ|ʔ|ʕ|ḏ|ḥ|ḷ|ṣ|ṭ|ṯ|ḅ|ḍ|ḳ|ẓ)'

/**
 * Convert search pattern with \c and \v shortcuts to proper regex
 */
export function expandRegexShortcuts(pattern: string): string {
    return pattern
        .replace(/\\v/gi, TUROYO_VOWELS)
        .replace(/\\c/gi, TUROYO_CONSONANTS)
}

/**
 * Check if a pattern contains regex special characters or shortcuts
 */
export function isRegexPattern(pattern: string): boolean {
    // Check for \c or \v shortcuts
    if (/\\[cv]/i.test(pattern)) {
        return true
    }

    // Check for common regex metacharacters
    const regexMetaChars = /[.*+?^${}()|[\]]/
    return regexMetaChars.test(pattern)
}

/**
 * Create a RegExp from a pattern with \c and \v shortcuts
 */
export function createSearchRegex(
    pattern: string,
    options: {
        caseSensitive?: boolean
    } = {}
): RegExp | null {
    const { caseSensitive = false } = options

    // Expand \c and \v shortcuts
    const expandedPattern = expandRegexShortcuts(pattern)

    // Build flags
    const flags = `${caseSensitive ? '' : 'i'}u` // always use unicode flag

    try {
        return new RegExp(expandedPattern, flags)
    }
    catch {
        return null
    }
}

/**
 * Test if a string matches a search pattern with \c and \v support
 */
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

    // If regex toggle is off, always do a plain-text includes match
    if (!useRegex) {
        return caseSensitive
            ? text.includes(pattern)
            : text.toLowerCase().includes(pattern.toLowerCase())
    }

    // Use regex matching
    const regex = createSearchRegex(pattern, { caseSensitive })
    if (!regex) {
    // If regex fails, fall back to simple includes
        return caseSensitive
            ? text.includes(pattern)
            : text.toLowerCase().includes(pattern.toLowerCase())
    }

    return regex.test(text)
}
