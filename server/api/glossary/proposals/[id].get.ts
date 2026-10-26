import { getEntry } from '~~/server/repositories/glossary/getEntry'
import { getProposal } from '~~/server/repositories/glossary/getProposal'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import type { IProposalDetail } from '#shared/types/IProposalDetail'

export default defineEventHandler(async (event): Promise<IProposalDetail> => {
    const proposal = await getProposal(getRouterParam(event, 'id', { decode: true }) || '')
    if (!proposal) throw createError({
        statusCode: 404,
        message: 'Proposal not found.',
    })
    const entry = await getEntry(proposal.entryId)
    await logUserActivity(event, {
        eventType: 'view_verb',
        query: proposal.entryId,
        resultCount: 1,
    })
    return {
        proposal,
        entry,
    }
})
