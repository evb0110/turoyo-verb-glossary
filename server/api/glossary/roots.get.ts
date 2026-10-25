import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'

export default defineEventHandler(async () => {
    const catalog = await getGlossaryCatalog()
    const roots = [...catalog.index]
    for (const proposal of catalog.proposals) {
        if (proposal.kind !== 'new-root' || roots.some(root => root.id === proposal.entryId)) continue
        roots.push({
            id: proposal.entryId,
            root: String(proposal.data.root || proposal.entryId.replaceAll('-', ' ')),
            homonym: null,
            stems: [],
            glossPreview: proposal.summary,
            exampleCount: 0,
            volume: '',
            proposed: true,
        })
    }
    return roots
})
