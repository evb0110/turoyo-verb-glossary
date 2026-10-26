import { getEntry } from '~~/server/repositories/glossary/getEntry'
import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getNewRootProposals } from '~~/server/repositories/glossary/getNewRootProposals'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { getTextIndex } from '~~/server/repositories/glossary/getTextIndex'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import { buildRootIndex } from '~~/server/services/glossary/buildRootIndex'
import { rootNeighbours } from '~~/server/services/glossary/rootNeighbours'

export default defineEventHandler(async (event) => {
    const id = getRouterParam(event, 'id', { decode: true }) || ''
    const entry = await getEntry(id)
    const proposals = await getEntryProposals(id)
    if (!entry && !proposals.some(proposal => proposal.kind === 'new-root')) {
        throw createError({
            statusCode: 404,
            message: 'Entry not found.',
        })
    }
    await logUserActivity(event, {
        eventType: 'view_verb',
        query: id,
        resultCount: 1,
    })
    const roots = buildRootIndex(await getEntryIndex(), await getProposalIndex(), await getNewRootProposals())
    return {
        entry,
        proposals,
        textIds: (await getTextIndex()).map(text => text.id),
        ...rootNeighbours(roots, id),
    }
})
