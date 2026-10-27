// The letter a root is listed under: its first character, as the glossary list groups it.
export function rootLetter(root: string): string {
    return [...root][0] || '?'
}
