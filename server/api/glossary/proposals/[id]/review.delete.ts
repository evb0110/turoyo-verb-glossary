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
    const removed = await undoProposalReview(
        body.reviewId,
        getRouterParam(event, 'id', { decode: true }) || '',
        user.id
    )
    if (!removed)
        throw createError({
            statusCode: 409,
            message:
        'Only your latest decision can be undone. Reload to see the current decision.',
        })
    return { undone: removed }
})
