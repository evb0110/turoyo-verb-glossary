/**
 * Reusable text manipulation utilities
 */

/**
 * Extract context around a match position with ellipsis handling
 * @param text - Full text to extract from
 * @param matchPos - Position of the match in the text
 * @param matchLength - Length of the matched text
 * @param contextLength - Number of characters to include before/after match
 * @returns Context string with ellipsis if truncated
 */
export function extractContext(
    text: string,
    matchPos: number,
    matchLength: number,
    contextLength: number = 50
): string {
    const start = Math.max(0, matchPos - contextLength)
    const end = Math.min(text.length, matchPos + matchLength + contextLength)

    let context = text.slice(start, end)

    // Add ellipsis if we truncated
    if (start > 0) {
        context = '...' + context
    }
    if (end < text.length) {
        context = context + '...'
    }

    return context
}

/**
 * Truncate text to a maximum length with ellipsis
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis if needed
 */
export function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
}

/**
 * Convert an array of token objects to a single string
 * @param tokens - Array of tokens with text property
 * @returns Concatenated text string
 */
export function tokenTextToString(tokens: Array<{ text: string }>): string {
    return tokens.map(token => token.text).join('')
}
