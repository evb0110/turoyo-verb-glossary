/**
 * Lightweight wrapper around the CSS Custom Highlight API.
 * Uses feature detection and no-ops on unsupported browsers.
 */

function isSupported(): boolean {
    return typeof window !== 'undefined'
        && typeof CSS !== 'undefined'
        && 'highlights' in CSS
        && 'Highlight' in window
}

export function setHighlights(name: string, _root: ParentNode, ranges: Array<{ startNode: Node, startOffset: number, endNode: Node, endOffset: number }>) {
    if (!isSupported()) return

    try {
        // Remove existing highlight with the same name
        const existing = CSS.highlights.get(name)
        if (existing) CSS.highlights.delete(name)

        const highlight = new window.Highlight()
        for (const r of ranges) {
            const range = new Range()
            range.setStart(r.startNode, r.startOffset)
            range.setEnd(r.endNode, r.endOffset)
            highlight.add(range)
        }

        CSS.highlights.set(name, highlight)
    }
    catch {
        // Silently ignore if constructing ranges fails (browser compatibility)
    }
}

export function clearHighlights(name: string) {
    if (!isSupported()) return
    try {
        if (CSS.highlights.has(name)) {
            CSS.highlights.delete(name)
        }
    }
    catch {
        // Silently ignore if clearing fails (browser compatibility)
    }
}

/**
 * Find text ranges matching a string (case-insensitive optional) within a root element.
 * This ignores hidden elements by checking offsetHeight/Width.
 */
export function findTextRanges(root: ParentNode, query: string, opts: { caseSensitive?: boolean } = {}) {
    const { caseSensitive = false } = opts
    const ranges: Array<{ startNode: Node, startOffset: number, endNode: Node, endOffset: number }> = []
    if (!query) return ranges

    const needle = caseSensitive ? query : query.toLowerCase()

    const walker = document.createTreeWalker(root as Node, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
            const parent = (node as Text).parentElement
            if (!parent) return NodeFilter.FILTER_REJECT
            const style = window.getComputedStyle(parent)
            if (style.visibility === 'hidden' || style.display === 'none') return NodeFilter.FILTER_REJECT
            if (parent.offsetHeight === 0 || parent.offsetWidth === 0) return NodeFilter.FILTER_SKIP
            return NodeFilter.FILTER_ACCEPT
        }
    })

    let textNode: Node | null
    while ((textNode = walker.nextNode())) {
        const text = (textNode as Text).data
        if (!text) continue
        const hay = caseSensitive ? text : text.toLowerCase()

        let from = 0
        while (true) {
            const idx = hay.indexOf(needle, from)
            if (idx === -1) break
            ranges.push({ startNode: textNode, startOffset: idx, endNode: textNode, endOffset: idx + needle.length })
            from = idx + needle.length
        }
    }

    return ranges
}

export function findRegexRanges(root: ParentNode, regex: RegExp) {
    const ranges: Array<{ startNode: Node, startOffset: number, endNode: Node, endOffset: number }> = []
    if (!(regex instanceof RegExp)) return ranges

    // Ensure global flag for repeated matches
    const flags = regex.flags.includes('g') ? regex.flags : `g${regex.flags}`
    const globalRe = new RegExp(regex.source, flags)

    const walker = document.createTreeWalker(root as Node, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
            const parent = (node as Text).parentElement
            if (!parent) return NodeFilter.FILTER_REJECT
            const style = window.getComputedStyle(parent)
            if (style.visibility === 'hidden' || style.display === 'none') return NodeFilter.FILTER_REJECT
            if (parent.offsetHeight === 0 || parent.offsetWidth === 0) return NodeFilter.FILTER_SKIP
            return NodeFilter.FILTER_ACCEPT
        }
    })

    let textNode: Node | null
    while ((textNode = walker.nextNode())) {
        const text = (textNode as Text).data
        if (!text) continue

        globalRe.lastIndex = 0
        let match: RegExpExecArray | null
        while ((match = globalRe.exec(text)) !== null) {
            const matched = match[0] ?? ''
            const start = match.index
            const end = start + matched.length
            if (matched.length === 0) {
                // Avoid infinite loops on zero-length matches
                globalRe.lastIndex += 1
                continue
            }
            ranges.push({ startNode: textNode, startOffset: start, endNode: textNode, endOffset: end })
        }
    }

    return ranges
}
