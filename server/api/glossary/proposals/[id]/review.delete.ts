import { getProposalReview } from '~~/server/repositories/reviews/getProposalReview'
import { undoProposalReview } from '~~/server/repositories/reviews/undoProposalReview'
import { requireApproved } from '~~/server/services/auth/requireApproved'

export default defineEventHandler(async (event) => {
    const user = await requireApproved(event)
    const body = await readBody<{ reviewId?: unknown }>(event)
    if (typeof body?.reviewId !== 'string' || !body.reviewId)
        throw createError({
            statusCode: 400,
            message: 'A saved decision is required.',
        })
    const proposalId = getRouterParam(event, 'id', { decode: true }) || ''
    const removed = await undoProposalReview(body.reviewId, proposalId, user.id)
    if (!removed)
        throw createError({
            statusCode: 409,
            message:
        'Only your latest decision can be undone. Reload to see the current decision.',
        })
    // The decision now in force (an earlier one may be restored). The undo is already committed,
    // so a failed read leaves it out and the client reloads the decisions instead.
    const current = await getProposalReview(proposalId).catch(() => undefined)
    return {
        undone: removed,
        current,
    }
})
