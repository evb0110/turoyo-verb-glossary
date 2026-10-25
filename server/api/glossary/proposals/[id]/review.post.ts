import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import { saveProposalReview } from '~~/server/repositories/reviews/saveProposalReview'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import { requireApproved } from '~~/server/services/auth/requireApproved'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

export default defineEventHandler(async (event) => {
    const user = await requireApproved(event)
    const body = await readBody<{ verdict?: unknown
        comment?: unknown }>(event)
    if (!body || !['accept', 'reject', 'discuss'].includes(String(body.verdict))) {
        throw createError({
            statusCode: 400,
            message: 'Choose accept, reject or discuss.',
        })
    }
    if (body.comment !== undefined && body.comment !== null && typeof body.comment !== 'string') {
        throw createError({
            statusCode: 400,
            message: 'Comment must be text.',
        })
    }
    const comment = typeof body.comment === 'string' ? body.comment.trim() : ''
    if (comment.length > 5000) throw createError({
        statusCode: 400,
        message: 'Comment is too long (maximum 5000).',
    })
    const proposal = (await getGlossaryCatalog()).proposals.find(item => item.id === getRouterParam(event, 'id', { decode: true }))
    if (!proposal) throw createError({
        statusCode: 404,
        message: 'Proposal not found.',
    })
    const review = await saveProposalReview({
        proposalId: proposal.id,
        entryId: proposal.entryId,
        userId: user.id,
        userName: user.name,
        verdict: body.verdict as TReviewVerdict,
        comment: comment || null,
    })
    await logUserActivity(event, {
        eventType: 'view_verb',
        query: proposal.entryId,
        metadata: {
            action: 'proposal_review',
            proposalId: proposal.id,
            verdict: review.verdict,
        },
    })
    return review
})
