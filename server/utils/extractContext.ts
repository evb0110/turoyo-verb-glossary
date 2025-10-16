export function extractContext(
    text: string,
    matchPos: number,
    matchLength: number,
    contextLength: number = 50
): string {
    const start = Math.max(0, matchPos - contextLength)
    const end = Math.min(text.length, matchPos + matchLength + contextLength)

    let context = text.slice(start, end)

    if (start > 0) {
        context = '...' + context
    }
    if (end < text.length) {
        context = context + '...'
    }

    return context
}
