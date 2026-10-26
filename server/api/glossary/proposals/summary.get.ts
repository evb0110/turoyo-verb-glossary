import { getMatchingProposals } from '~~/server/repositories/glossary/getMatchingProposals'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { getProposalReviews } from '~~/server/repositories/reviews/getProposalReviews'
import { requireApproved } from '~~/server/services/auth/requireApproved'
import { summarizeProposals } from '~~/server/services/glossary/summarizeProposals'

export default defineEventHandler(async (event) => {
    const user = await requireApproved(event)
    const query = getQuery(event)
    const reviews = await getProposalReviews()
    const matching = await getMatchingProposals({
        root: String(query.root || ''),
        text: String(query.text || ''),
    })
    return summarizeProposals(
        await getProposalIndex(), matching, reviews, user.id,
        String(query.resume || ''), String(query.resumeGroup || '')
    )
})
