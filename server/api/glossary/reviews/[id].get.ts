import { getProposalReviewHistory } from '~~/server/repositories/reviews/getProposalReviewHistory'
import { requireApproved } from '~~/server/services/auth/requireApproved'

export default defineEventHandler(async (event) => {
    await requireApproved(event)
    setResponseHeader(event, 'Cache-Control', 'private, no-store')
    return getProposalReviewHistory(getRouterParam(event, 'id', { decode: true }) || '')
})
