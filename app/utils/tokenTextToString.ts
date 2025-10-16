export function tokenTextToString(tokens: Array<{ text: string }>) {
    return tokens.map(token => token.text).join('')
}
