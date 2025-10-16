interface TextSegment {
    text: string
    isMatch: boolean
}

function createSearchRegex(query: string, opts: { caseSensitive?: boolean } = {}): RegExp | null {
    const { caseSensitive = false } = opts

    try {
        const flags = caseSensitive ? 'g' : 'gi'
        return new RegExp(query.replace(/[|\\{}()[\]^$+*?.]/g, '\\$&'), flags)
    }
    catch {
        return null
    }
}

export function parseHighlights(
    text: string,
    query: string,
    opts: {
        useRegex?: boolean
        caseSensitive?: boolean
    } = {}
): TextSegment[] {
    if (!text || !query) {
        return [{ text, isMatch: false }]
    }

    const { useRegex = false, caseSensitive = false } = opts

    try {
        if (useRegex) {
            const regex = createSearchRegex(query, { caseSensitive })
            if (!regex) {
                return [{ text, isMatch: false }]
            }
            return parseWithRegex(text, regex)
        }
        else {
            return parseWithPlainText(text, query, caseSensitive)
        }
    }
    catch {
        return [{ text, isMatch: false }]
    }
}

function parseWithPlainText(text: string, query: string, caseSensitive: boolean): TextSegment[] {
    const segments: TextSegment[] = []
    const searchText = caseSensitive ? text : text.toLowerCase()
    const searchQuery = caseSensitive ? query : query.toLowerCase()

    let lastIndex = 0
    let index = searchText.indexOf(searchQuery, lastIndex)

    while (index !== -1) {
        if (index > lastIndex) {
            segments.push({ text: text.slice(lastIndex, index), isMatch: false })
        }

        const matchText = text.slice(index, index + query.length)
        segments.push({ text: matchText, isMatch: true })

        lastIndex = index + query.length
        index = searchText.indexOf(searchQuery, lastIndex)
    }

    if (lastIndex < text.length) {
        segments.push({ text: text.slice(lastIndex), isMatch: false })
    }

    return segments
}

function parseWithRegex(text: string, regex: RegExp): TextSegment[] {
    const segments: TextSegment[] = []

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
            segments.push({ text: text.slice(lastIndex, matchIndex), isMatch: false })
        }

        segments.push({ text: matchText, isMatch: true })

        lastIndex = matchIndex + matchText.length
    }

    if (lastIndex < text.length) {
        segments.push({ text: text.slice(lastIndex), isMatch: false })
    }

    return segments
}
