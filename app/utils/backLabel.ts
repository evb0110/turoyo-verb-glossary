// Names the in-app page a history entry points to, for a "Back to …" link.
export function backLabel(path: string) {
    let url: URL
    let segments: string[]
    try {
        url = new URL(path, 'https://glossary.invalid')
        segments = url.pathname.split('/').filter(Boolean).map(segment => decodeURIComponent(segment))
    }
    catch {
        return 'Back'
    }
    const [page, id] = segments
    if (page === 'entry' && id) return `Back to ${id.replaceAll('-', ' ')}`
    if (page === 'texts' && id) {
        const verse = url.searchParams.get('v')
        return `Back to text ${id}${verse ? `, verse ${verse}` : ''}`
    }
    if (page === 'texts') return 'Back to texts'
    if (page === 'review') return 'Back to review'
    if (page === 'glossary') {
        const query = url.searchParams.get('q')
        return query ? `Back to search “${query}”` : 'Back to glossary'
    }
    if (page === 'research') return 'Back to research notes'
    if (!page) return 'Back to start'
    return 'Back'
}
