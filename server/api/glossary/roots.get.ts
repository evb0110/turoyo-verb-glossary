import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'

export default defineEventHandler(async (event) => {
    const roots = [...await getEntryIndex()]
    const known = new Set(roots.map(root => root.id))
    const newRoots = new Set((await getProposalIndex())
        .filter(row => row.kind === 'new-root' && !known.has(row.entryId))
        .map(row => row.entryId))
    for (const entryId of newRoots) {
        const proposal = (await getEntryProposals(entryId)).find(item => item.kind === 'new-root')
        if (!proposal) continue
        roots.push({
            id: entryId,
            root: String(proposal.data.root || entryId.replaceAll('-', ' ')),
            homonym: null,
            stems: [],
            glossPreview: proposal.summary,
            exampleCount: 0,
            volume: '',
            proposed: true,
        })
    }
    // Glossary data changes only with a deploy; keep it in the browser for a few minutes.
    setResponseHeader(event, 'cache-control', 'private, max-age=600')
    return roots
})
