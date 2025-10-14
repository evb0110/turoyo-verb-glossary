import { createSearchRegex } from './regexSearch'

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
            if (!regex) {
                return escapeHtml(text)
            }
            return highlightWithRegex(text, regex)
        }
        else {
            return highlightWithPlainText(text, query, caseSensitive)
        }
    }
    catch {
        return escapeHtml(text)
    }
}

function highlightWithPlainText(text: string, query: string, caseSensitive: boolean): string {
    const parts: string[] = []
    const searchText = caseSensitive ? text : text.toLowerCase()
    const searchQuery = caseSensitive ? query : query.toLowerCase()

    let lastIndex = 0
    let index = searchText.indexOf(searchQuery, lastIndex)

    while (index !== -1) {
        if (index > lastIndex) {
            parts.push(escapeHtml(text.slice(lastIndex, index)))
        }

        const matchText = text.slice(index, index + query.length)
        parts.push(`<mark class="highlight-match">${escapeHtml(matchText)}</mark>`)

        lastIndex = index + query.length
        index = searchText.indexOf(searchQuery, lastIndex)
    }

    if (lastIndex < text.length) {
        parts.push(escapeHtml(text.slice(lastIndex)))
    }

    return parts.join('')
}

function highlightWithRegex(text: string, regex: RegExp): string {
    const parts: string[] = []

    const flags = regex.flags.includes('g') ? regex.flags : `g${regex.flags}`
    const globalRegex = new RegExp(regex.source, flags)

    let lastIndex = 0
    let match: RegExpExecArray | null

    while ((match = globalRegex.exec(text)) !== null) {
        const matchText = match[0]
        const matchIndex = match.index

        if (matchText.length === 0) {
            globalRegex.lastIndex += 1
            continue
        }

        if (matchIndex > lastIndex) {
            parts.push(escapeHtml(text.slice(lastIndex, matchIndex)))
        }

        parts.push(`<mark class="highlight-match">${escapeHtml(matchText)}</mark>`)

        lastIndex = matchIndex + matchText.length
    }

    if (lastIndex < text.length) {
        parts.push(escapeHtml(text.slice(lastIndex)))
    }

    return parts.join('')
}

function escapeHtml(text: string): string {
    const htmlEscapes: Record<string, string> = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        '\'': '&#39;'
    }

    return text.replace(/[&<>"']/g, char => htmlEscapes[char] || char)
}
