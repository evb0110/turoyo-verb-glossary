import { getProposalReviews } from '~~/server/repositories/reviews/getProposalReviews'
import { requireApproved } from '~~/server/services/auth/requireApproved'

export default defineEventHandler(async (event) => {
    await requireApproved(event)
    setResponseHeader(event, 'Cache-Control', 'private, no-store')
    return getProposalReviews()
})
