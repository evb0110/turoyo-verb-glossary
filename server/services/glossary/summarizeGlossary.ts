import type { IEntryIndex } from '#shared/types/IEntryIndex'
import type { IProposalIndex } from '#shared/types/IProposalIndex'
import type { ITextIndex } from '#shared/types/ITextIndex'

export function summarizeGlossary(index: IEntryIndex[], textIndex: ITextIndex[], proposals: IProposalIndex[]) {
    const kinds: Record<string, number> = {}
    for (const proposal of proposals) kinds[proposal.kind] = (kinds[proposal.kind] || 0) + 1
    return {
        entries: index.length,
        texts: textIndex.length,
        read: textIndex.filter(text => text.reading === 'read').length,
        partial: textIndex.filter(text => text.reading === 'partial').length,
        collections: [...new Set(textIndex.map(text => text.collection))].map((collection) => {
            const texts = textIndex.filter(text => text.collection === collection)
            return {
                collection,
                total: texts.length,
                read: texts.filter(text => text.reading === 'read').length,
                partial: texts.filter(text => text.reading === 'partial').length,
                unread: texts.filter(text => text.reading === 'unread').length,
            }
        }),
        proposals: proposals.length,
        kinds,
    }
}
