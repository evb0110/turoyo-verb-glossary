export function tokenTextToString(tokens: Array<{ text: string }>): string {
    return tokens.map(token => token.text).join('')
}
