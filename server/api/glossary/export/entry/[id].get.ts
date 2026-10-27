import { getEntry } from '~~/server/repositories/glossary/getEntry'
import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getProposalReviews } from '~~/server/repositories/reviews/getProposalReviews'
import { buildEntryDocument } from '~~/server/services/export/buildEntryDocument'
import { exportContext } from '~~/server/utils/exportContext'
import { readExportFormat } from '~~/server/utils/readExportFormat'
import { sendDocument } from '~~/server/utils/sendDocument'

// One entry; ?suggestions=1 adds its machine suggestions with the current team decisions.
export default defineEventHandler(async (event) => {
    const format = readExportFormat(event)
    const id = getRouterParam(event, 'id', { decode: true }) || ''
    const withSuggestions = getQuery(event).suggestions === '1'
    const entry = await getEntry(id)
    const proposals = await getEntryProposals(id)
    if (!entry && !proposals.some(proposal => proposal.kind === 'new-root'))
        throw createError({
            statusCode: 404,
            message: 'Entry not found.',
        })
    const ids = new Set(proposals.map(proposal => proposal.id))
    const reviews = withSuggestions
        ? new Map((await getProposalReviews()).filter(review => ids.has(review.proposalId))
                .map(review => [review.proposalId, review]))
        : new Map()
    return sendDocument(event, format, {
        key: `entry:${id}:${withSuggestions ? 'suggestions' : ''}`,
        // The suggestions carry the team's decisions: their revision is the decisions on this entry.
        revision: withSuggestions ? JSON.stringify([...reviews.values()]) : '',
        build: async () => buildEntryDocument({
            id,
            entry,
            proposals: withSuggestions ? proposals : null,
            reviews,
            context: exportContext(event),
        }),
    })
})
