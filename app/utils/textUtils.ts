export function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
}

export function tokenTextToString(tokens: Array<{ text: string }>): string {
    return tokens.map(token => token.text).join('')
}
