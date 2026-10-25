import { getProposalReviews } from '~~/server/repositories/reviews/getProposalReviews'

export default defineEventHandler(async () => getProposalReviews())
