/**
 * Utility functions for generating search filter options
 */

// Minimal metadata needed for filtering
interface FilterableVerb {
    root: string
    etymology_sources: string[]
    stems: string[]
}

export interface SelectOption {
    label: string
    value: string | null
}

/**
 * Generate letter filter options from search results
 */
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

/**
 * Generate etymology filter options from search results
 */
export function generateEtymologyOptions(results: FilterableVerb[]): SelectOption[] {
    if (results.length === 0) {
        return [{ label: 'All etymologies', value: null }]
    }

    const etymCounts = new Map<string, number>()
    results.forEach((v) => {
        const sources = v.etymology_sources?.length ? v.etymology_sources : ['Unknown']
        sources.forEach((source) => {
            // Filter out null/undefined values
            if (source && source !== 'null' && source !== 'undefined') {
                etymCounts.set(source, (etymCounts.get(source) || 0) + 1)
            }
        })
    })

    return [
        { label: 'All etymologies', value: null },
        ...Array.from(etymCounts.entries())
            .sort(([a], [b]) => (a || '').localeCompare(b || ''))
            .map(([source, count]) => ({ label: `${source} (${count})`, value: source }))
    ]
}

/**
 * Generate stem filter options from search results
 */
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

/**
 * Apply filters to verb metadata
 */
export function applyFilters(
    results: FilterableVerb[],
    filters: {
        letter: string | null
        etymology: string | null
        stem: string | null
    }
): FilterableVerb[] {
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
