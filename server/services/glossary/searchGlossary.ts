import { Script, createContext } from 'node:vm'
import type { ISearchDocument } from '#shared/types/ISearchDocument'
import type { ISearchResult } from '#shared/types/ISearchResult'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

// Regular expressions backtrack, and some patterns that pass the checks below still take minutes on a
// long verse. The search runs under V8's watchdog, which stops it after the limit, so one query
// cannot hold up the server.
const REGEX_LIMIT_MS = 3000
const watched = createContext({ task: () => {} })
const runTask = new Script('task()')

function underWatchdog<T>(task: () => T): T {
    watched.task = task
    try {
        return runTask.runInContext(watched, { timeout: REGEX_LIMIT_MS }) as T
    }
    catch (error) {
        if ((error as { code?: string }).code === 'ERR_SCRIPT_EXECUTION_TIMEOUT')
            throw new Error('This expression takes too long to search. Make it more specific, for example with ^ or fewer .*.')
        throw error
    }
    finally {
        watched.task = () => {}
    }
}

export function searchGlossary(documents: ISearchDocument[], query: string, regex: boolean) {
    if (query.length > 160) throw new Error('Search is limited to 160 characters.')
    // Limit dangerous regular-expression constructs before evaluating over the corpus.
    if (regex && (/\)[+*{]/u.test(query) || /\\[1-9]|\(\?[=!<]/u.test(query)
        || /(?:\.\*){2}|(?:\.\+){2}/u.test(query))) {
        throw new Error('Use a simple expression without nested repetitions, lookarounds or backreferences.')
    }
    const pattern = regex ? new RegExp(query, 'iu') : null
    const normalized = normalizeTuroyo(query)
    if (!regex && !normalized) return {
        results: [],
        counts: {},
        total: 0,
    }
    const results: ISearchResult[] = []
    const counts: Record<string, number> = {}
    const scan = () => {
        for (const doc of documents) {
            const match = pattern?.exec(doc.text)
            const position = pattern ? match?.index ?? -1 : doc.normalized.indexOf(normalized)
            if (position < 0) continue
            counts[doc.type] = (counts[doc.type] || 0) + 1
            if (results.filter(result => result.type === doc.type).length >= 30) continue
            // Map normalized offsets back onto original text, preserving combining marks and removed joiners.
            const offsets: number[] = []
            let originalOffset = 0
            for (const part of doc.text.matchAll(/\P{M}\p{M}*|\p{M}+/gu)) {
                for (const _char of normalizeTuroyo(part[0])) offsets.push(originalOffset)
                originalOffset += part[0].length
            }
            const start = pattern ? position : offsets[position] ?? position
            const length = pattern
                ? match?.[0].length || 0
                : (offsets[position + normalized.length] ?? doc.text.length) - start
            const left = Math.max(0, start - 70)
            const snippet = doc.text.slice(left, Math.max(start + length + 100, left + 200))
            results.push({
                id: `${doc.type}:${doc.id}`,
                type: doc.type,
                title: doc.title,
                snippet: `${left ? '…' : ''}${snippet}`,
                to: doc.to,
                ranges: [[start - left + (left ? 1 : 0), start - left + length + (left ? 1 : 0)]],
            })
        }
    }
    if (pattern) underWatchdog(scan)
    else scan()
    return {
        results,
        counts,
        total: Object.values(counts).reduce((sum, n) => sum + n, 0),
    }
}
