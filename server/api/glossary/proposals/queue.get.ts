import { getMatchingProposals } from '~~/server/repositories/glossary/getMatchingProposals'
import { buildProposalQueue } from '~~/server/services/glossary/buildProposalQueue'

export default defineEventHandler(async (event) => {
    const query = getQuery(event)
    return buildProposalQueue(await getMatchingProposals({
        root: String(query.root || ''),
        text: String(query.text || ''),
    }), String(query.group || ''), String(query.proposal || ''))
})
