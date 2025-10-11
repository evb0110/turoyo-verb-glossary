/**
 * Regex search utilities for Turoyo text
 * Supports custom shortcuts: \c for consonants, \v for vowels
 */

// Turoyo vowels pattern
// Based on actual character usage in the verb corpus
const TUROYO_VOWELS = '(?:a|e|i|o|u|ə|ǝ|é|ī|á|í|ó|ú|ā|ē|ō|ū)'

// Turoyo consonants pattern
// Based on actual character usage in the verb corpus
const TUROYO_CONSONANTS = '(?:b|d|f|g|h|k|l|m|n|p|q|r|s|t|v|w|x|y|z|č|ġ|š|ž|ǧ|ʔ|ʕ|ḏ|ḥ|ḷ|ṣ|ṭ|ṯ|ḅ|ḍ|ḳ|ẓ)'

/**
 * Convert search pattern with \c and \v shortcuts to proper regex
 * \c is replaced with Turoyo consonants pattern
 * \v is replaced with Turoyo vowels pattern
 *
 * @param pattern - Search pattern with optional \c and \v shortcuts
 * @returns Pattern with shortcuts expanded to character classes
 *
 * @example
 * expandRegexShortcuts('b\\vd') // → 'b(?:a|e|i|o|u|ə|ǝ|é|ī)d'
 * expandRegexShortcuts('\\c\\v\\c') // → '(?:b|d|f|...)(?:a|e|i|...)(?:b|d|f|...)'
 */
export function expandRegexShortcuts(pattern: string): string {
    return pattern
        .replace(/\\v/gi, TUROYO_VOWELS)
        .replace(/\\c/gi, TUROYO_CONSONANTS)
}

/**
 * Check if a pattern contains regex special characters or shortcuts
 * This helps determine if regex mode should be used
 *
 * @param pattern - Search pattern to check
 * @returns true if pattern appears to use regex syntax
 */
export function isRegexPattern(pattern: string): boolean {
    // Check for \c or \v shortcuts
    if (/\\[cv]/i.test(pattern)) {
        return true
    }

    // Check for common regex metacharacters
    // Note: We need to be careful not to match literal dots in normal text
    const regexMetaChars = /[.*+?^${}()|[\]]/
    return regexMetaChars.test(pattern)
}

/**
 * Create a RegExp from a pattern with \c and \v shortcuts
 * Handles both regex patterns and plain text search
 *
 * @param pattern - Search pattern
 * @param options - Regex flags options
 * @returns RegExp object ready to use for matching
 *
 * @throws Error if the regex pattern is invalid
 */
export function createSearchRegex(
    pattern: string,
    options: {
        caseSensitive?: boolean
        wholeWord?: boolean
    } = {}
): RegExp {
    const { caseSensitive = false, wholeWord = false } = options

    // Expand \c and \v shortcuts
    let expandedPattern = expandRegexShortcuts(pattern)

    // Add word boundaries if requested
    if (wholeWord) {
        expandedPattern = `\\b${expandedPattern}\\b`
    }

    // Build flags
    const flags = `${caseSensitive ? '' : 'i'}u` // always use unicode flag

    try {
        return new RegExp(expandedPattern, flags)
    }
    catch (error) {
        throw new Error(`Invalid regex pattern: ${pattern}. ${error instanceof Error ? error.message : ''}`)
    }
}

/**
 * Test if a string matches a search pattern with \c and \v support
 *
 * @param text - Text to search in
 * @param pattern - Search pattern (supports \c and \v)
 * @param options - Search options
 * @returns true if the pattern matches the text
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
    try {
        const regex = createSearchRegex(pattern, { caseSensitive })
        return regex.test(text)
    }
    catch {
    // If regex fails, fall back to simple includes
        return caseSensitive
            ? text.includes(pattern)
            : text.toLowerCase().includes(pattern.toLowerCase())
    }
}

/**
 * Create a global version of a regex for multiple matches
 * @param regex - Original regex pattern
 * @returns Regex with global flag enabled
 */
export function makeGlobalRegex(regex: RegExp): RegExp {
    const flags = regex.flags.includes('g') ? regex.flags : `g${regex.flags}`
    return new RegExp(regex.source, flags)
}

/**
 * Iterator that safely handles zero-length matches
 * Prevents infinite loops when matching patterns like `\b` or `(?=...)`
 * @param text - Text to search in
 * @param regex - Regular expression to match
 * @yields RegExpExecArray for each match
 */
export function* matchAll(text: string, regex: RegExp): Generator<RegExpExecArray> {
    const globalRegex = makeGlobalRegex(regex)
    let match: RegExpExecArray | null

    while ((match = globalRegex.exec(text)) !== null) {
        yield match
        // Prevent infinite loop on zero-length matches
        if (match[0].length === 0) {
            globalRegex.lastIndex += 1
        }
    }
}

/**
 * Get helpful examples for regex shortcuts
 */
export const REGEX_EXAMPLES = [
    { pattern: '\\c\\v\\c', description: 'Any consonant-vowel-consonant pattern (e.g., "bdy", "ktb")' },
    { pattern: 'b\\vd', description: 'Words with "b" + vowel + "d" (e.g., "bdy", "bod")' },
    { pattern: '^\\c\\c\\c$', description: 'Exactly three consonants (e.g., "bdy", "ktb")' },
    { pattern: 'ʕ\\v', description: 'ʕ followed by any vowel' },
    { pattern: '\\vl$', description: 'Ends with vowel + "l"' }
] as const
