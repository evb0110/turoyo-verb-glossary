/**
 * Server-side text highlighting using HTML mark tags
 * Works in both SSR and client environments
 */

import { createSearchRegex } from './regexSearch'

/**
 * Highlight all matches in text by wrapping them in <mark> tags
 * Escapes HTML to prevent XSS
 */
export function highlightMatches(
    text: string,
    query: string,
    opts: {
        useRegex?: boolean
        caseSensitive?: boolean
    } = {}
): string {
    if (!text || !query) return escapeHtml(text)

    const { useRegex = false, caseSensitive = false } = opts

    try {
        if (useRegex) {
            const regex = createSearchRegex(query, { caseSensitive })
            return highlightWithRegex(text, regex)
        } else {
            return highlightWithPlainText(text, query, caseSensitive)
        }
    } catch (e) {
        // If highlighting fails, return escaped text without highlights
        return escapeHtml(text)
    }
}

/**
 * Highlight using plain text search
 */
function highlightWithPlainText(text: string, query: string, caseSensitive: boolean): string {
    const parts: string[] = []
    const searchText = caseSensitive ? text : text.toLowerCase()
    const searchQuery = caseSensitive ? query : query.toLowerCase()

    let lastIndex = 0
    let index = searchText.indexOf(searchQuery, lastIndex)

    while (index !== -1) {
        // Add text before match (escaped)
        if (index > lastIndex) {
            parts.push(escapeHtml(text.slice(lastIndex, index)))
        }

        // Add highlighted match
        const matchText = text.slice(index, index + query.length)
        parts.push(`<mark class="highlight-match">${escapeHtml(matchText)}</mark>`)

        lastIndex = index + query.length
        index = searchText.indexOf(searchQuery, lastIndex)
    }

    // Add remaining text (escaped)
    if (lastIndex < text.length) {
        parts.push(escapeHtml(text.slice(lastIndex)))
    }

    return parts.join('')
}

/**
 * Highlight using regex search
 */
function highlightWithRegex(text: string, regex: RegExp): string {
    const parts: string[] = []

    // Ensure global flag
    const flags = regex.flags.includes('g') ? regex.flags : `g${regex.flags}`
    const globalRegex = new RegExp(regex.source, flags)

    let lastIndex = 0
    let match: RegExpExecArray | null

    while ((match = globalRegex.exec(text)) !== null) {
        const matchText = match[0]
        const matchIndex = match.index

        // Avoid infinite loops on zero-length matches
        if (matchText.length === 0) {
            globalRegex.lastIndex += 1
            continue
        }

        // Add text before match (escaped)
        if (matchIndex > lastIndex) {
            parts.push(escapeHtml(text.slice(lastIndex, matchIndex)))
        }

        // Add highlighted match
        parts.push(`<mark class="highlight-match">${escapeHtml(matchText)}</mark>`)

        lastIndex = matchIndex + matchText.length
    }

    // Add remaining text (escaped)
    if (lastIndex < text.length) {
        parts.push(escapeHtml(text.slice(lastIndex)))
    }

    return parts.join('')
}

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text: string): string {
    const htmlEscapes: Record<string, string> = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }

    return text.replace(/[&<>"']/g, (char) => htmlEscapes[char] || char)
}
