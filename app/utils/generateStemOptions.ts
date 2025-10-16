import type { SelectOption } from '~/types/types/search'

interface FilterableVerb {
    root: string
    etymology_sources: string[]
    stems: string[]
}

export function generateStemOptions(results: FilterableVerb[]): SelectOption[] {
    if (results.length === 0) {
        return [{ label: 'All stems', value: null }]
    }

    const stemCounts = new Map<string, number>()
    results.forEach((v) => {
        v.stems.forEach((stem) => {
            stemCounts.set(stem, (stemCounts.get(stem) || 0) + 1)
        })
    })

    return [
        { label: 'All stems', value: null },
        ...Array.from(stemCounts.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''))
            .map(([stem, count]) => ({ label: `${stem} (${count})`, value: stem }))
    ]
}
