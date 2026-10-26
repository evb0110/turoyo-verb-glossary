import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import { getProposalReviews } from '~~/server/repositories/reviews/getProposalReviews'
import { requireApproved } from '~~/server/services/auth/requireApproved'
import { filterProposals } from '~~/server/services/glossary/filterProposals'
import { summarizeProposals } from '~~/server/services/glossary/summarizeProposals'

export default defineEventHandler(async (event) => {
    const user = await requireApproved(event)
    const query = getQuery(event)
    const catalog = await getGlossaryCatalog()
    const reviews = await getProposalReviews()
    const matching = filterProposals(catalog.proposals, catalog.index, {
        root: String(query.root || ''),
        text: String(query.text || ''),
    })
    return summarizeProposals(
        catalog.proposals, matching, reviews, user.id,
        String(query.resume || ''), String(query.resumeGroup || '')
    )
})
