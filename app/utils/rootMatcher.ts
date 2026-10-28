import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

// Tests a root's letters (without the homonym number, so "^ʔmr$" finds ʔmr 1 and ʔmr 2) against
// the search: a regular expression, or text found anywhere in the root with vowel and stress marks
// optional, as in the full search. Throws on an invalid expression.
export function rootMatcher(query: string, regex: boolean): (root: string) => boolean {
    const letters = (root: string) => root.replace(/\s+\d+$/u, '')
    if (regex) {
        const pattern = new RegExp(query, 'iu')
        return root => pattern.test(letters(root))
    }
    const normalized = normalizeTuroyo(query.trim())
    return root => normalizeTuroyo(letters(root)).includes(normalized)
}
