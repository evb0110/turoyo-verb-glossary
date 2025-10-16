import type { IFilterableVerb } from '~/types/IFilterableVerb'
import type { ISelectOption } from '~/types/ISelectOption'

export function generateLetterOptions(results: IFilterableVerb[]): ISelectOption[] {
    if (results.length === 0) {
        return [{
            label: 'All letters',
            value: null,
        }]
    }

    const letterCounts = new Map<string, number>()
    results.forEach((v) => {
        const letter = v.root?.[0]
        if (letter) {
            letterCounts.set(letter, (letterCounts.get(letter) || 0) + 1)
        }
    })

    return [
        {
            label: 'All letters',
            value: null,
        },
        ...Array.from(letterCounts.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''))
            .map(([letter, count]) => ({
                label: `${letter} (${count})`,
                value: letter,
            })),
    ]
}
