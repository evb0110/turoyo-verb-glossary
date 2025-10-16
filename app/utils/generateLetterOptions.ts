import type { SelectOption } from '~/types/types/search'

interface FilterableVerb {
    root: string
    etymology_sources: string[]
    stems: string[]
}

export function generateLetterOptions(results: FilterableVerb[]): SelectOption[] {
    if (results.length === 0) {
        return [{ label: 'All letters', value: null }]
    }

    const letterCounts = new Map<string, number>()
    results.forEach((v) => {
        const letter = v.root?.[0]
        if (letter) {
            letterCounts.set(letter, (letterCounts.get(letter) || 0) + 1)
        }
    })

    return [
        { label: 'All letters', value: null },
        ...Array.from(letterCounts.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''))
            .map(([letter, count]) => ({ label: `${letter} (${count})`, value: letter }))
    ]
}
