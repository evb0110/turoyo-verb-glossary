import type { IFilterableVerb } from '~/types/IFilterableVerb'
import type { ISelectOption } from '~/types/ISelectOption'

export function generateEtymologyOptions(results: IFilterableVerb[]): ISelectOption[] {
    if (results.length === 0) {
        return [{
            label: 'All etymologies',
            value: null,
        }]
    }

    const etymCounts = new Map<string, number>()
    results.forEach((v) => {
        const sources = v.etymology_sources?.length ? v.etymology_sources : ['Unknown']
        sources.forEach((source) => {
            if (source && source !== 'null' && source !== 'undefined') {
                etymCounts.set(source, (etymCounts.get(source) || 0) + 1)
            }
        })
    })

    return [
        {
            label: 'All etymologies',
            value: null,
        },
        ...Array.from(etymCounts.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''))
            .map(([source, count]) => ({
                label: `${source} (${count})`,
                value: source,
            })),
    ]
}
