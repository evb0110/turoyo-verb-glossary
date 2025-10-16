import type { IFilterableVerb } from '~/types/IFilterableVerb'
import type { ISelectOption } from '~/types/ISelectOption'

export function generateStemOptions(results: IFilterableVerb[]): ISelectOption[] {
    if (results.length === 0) {
        return [{
            label: 'All stems',
            value: null,
        }]
    }

    const stemCounts = new Map<string, number>()
    results.forEach((v) => {
        v.stems.forEach((stem) => {
            stemCounts.set(stem, (stemCounts.get(stem) || 0) + 1)
        })
    })

    return [
        {
            label: 'All stems',
            value: null,
        },
        ...Array.from(stemCounts.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''))
            .map(([stem, count]) => ({
                label: `${stem} (${count})`,
                value: stem,
            })),
    ]
}
