import type { IGlossaryCatalog } from '#shared/types/IGlossaryCatalog'

export function summarizeGlossary(catalog: IGlossaryCatalog) {
    const kinds: Record<string, number> = {}
    for (const proposal of catalog.proposals) kinds[proposal.kind] = (kinds[proposal.kind] || 0) + 1
    return {
        entries: catalog.index.length,
        texts: catalog.textIndex.length,
        read: catalog.textIndex.filter(text => text.reading === 'read').length,
        partial: catalog.textIndex.filter(text => text.reading === 'partial').length,
        collections: [...new Set(catalog.textIndex.map(text => text.collection))].map((collection) => {
            const texts = catalog.textIndex.filter(text => text.collection === collection)
            return {
                collection,
                total: texts.length,
                read: texts.filter(text => text.reading === 'read').length,
                partial: texts.filter(text => text.reading === 'partial').length,
                unread: texts.filter(text => text.reading === 'unread').length,
            }
        }),
        proposals: catalog.proposals.length,
        kinds,
    }
}
