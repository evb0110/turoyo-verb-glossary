export function entryHref(id: string, stemId?: string, sense?: string): string {
    const anchor = stemId ? `#${encodeURIComponent(stemId)}${sense ? `-sense-${encodeURIComponent(sense)}` : ''}` : ''
    return `/entry/${encodeURIComponent(id)}${anchor}`
}
