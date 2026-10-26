import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { getProposalReviews } from '~~/server/repositories/reviews/getProposalReviews'
import { requireApproved } from '~~/server/services/auth/requireApproved'
import { countUndecidedByEntry } from '~~/server/services/glossary/countUndecidedByEntry'

export default defineEventHandler(async (event) => {
    await requireApproved(event)
    setResponseHeader(event, 'cache-control', 'private, no-store')
    return countUndecidedByEntry(await getProposalIndex(), await getProposalReviews())
})
