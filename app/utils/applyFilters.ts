import type { IFilterableVerb } from '~/types/IFilterableVerb'

export function applyFilters(
    results: IFilterableVerb[],
    filters: {
        letter: string | null
        etymology: string | null
        stem: string | null
    }
) {
    let filtered = results

    if (filters.letter) {
        filtered = filtered.filter(v => v.root.startsWith(filters.letter as string))
    }

    if (filters.etymology) {
        filtered = filtered.filter(v =>
            v.etymology_sources?.includes(filters.etymology as string)
            || (!v.etymology_sources?.length && filters.etymology === 'Unknown')
        )
    }

    if (filters.stem) {
        filtered = filtered.filter(v => v.stems.includes(filters.stem as string))
    }

    return filtered
}
