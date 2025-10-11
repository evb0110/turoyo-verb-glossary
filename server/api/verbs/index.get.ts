import { matchesPattern } from '../../utils/regexSearch'

export default defineEventHandler(async (event) => {
    const query = getQuery(event)

    // Load search index (lightweight, single file)
    const searchIndex = await loadSearchIndex()
    const allVerbs = searchIndex.verbs || []

    // Apply filters
    let filtered = allVerbs

    // Filter by etymology source
    if (query.etymology) {
        const etymSource = String(query.etymology)
        filtered = filtered.filter(v =>
            v.etymology_sources && v.etymology_sources.includes(etymSource)
        )
    }

    // Filter by stem
    if (query.stem) {
        const stemFilter = String(query.stem)
        filtered = filtered.filter(v =>
            v.stems && v.stems.includes(stemFilter)
        )
    }

    // Filter by letter
    if (query.letter) {
        const letter = String(query.letter)
        filtered = filtered.filter(v => v.root.charAt(0) === letter)
    }

    // Search query
    if (query.q) {
        const searchQuery = String(query.q)
        const rootsOnly = query.rootsOnly === 'true'
        const useRegex = query.useRegex === 'true'
        const caseSensitive = query.caseSensitive === 'true'

        filtered = filtered.filter((v) => {
            // Search in root (supports regex with \c and \v)
            if (matchesPattern(v.root, searchQuery, { useRegex, caseSensitive })) return true

            // If roots only, stop here
            if (rootsOnly) return false

            // Search in forms (supports regex with \c and \v)
            if (v.forms && v.forms.some(f => matchesPattern(f, searchQuery, { useRegex, caseSensitive }))) return true

            // Note: Translation search not available in search index
            // Users need to search by root/form only

            return false
        })
    }

    // Search index already has the right format, just return it
    setHeader(event, 'content-type', 'application/json; charset=utf-8')
    return {
        total: filtered.length,
        verbs: filtered
    }
})
