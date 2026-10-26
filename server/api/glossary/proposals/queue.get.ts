import { getGlossaryCatalog } from '~~/server/repositories/glossary/getGlossaryCatalog'
import { buildProposalQueue } from '~~/server/services/glossary/buildProposalQueue'
import { filterProposals } from '~~/server/services/glossary/filterProposals'

export default defineEventHandler(async (event) => {
    const query = getQuery(event)
    const catalog = await getGlossaryCatalog()
    return buildProposalQueue(filterProposals(catalog.proposals, catalog.index, {
        root: String(query.root || ''),
        text: String(query.text || ''),
    }), String(query.group || ''), String(query.proposal || ''))
})
