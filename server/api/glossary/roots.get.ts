import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getNewRootProposals } from '~~/server/repositories/glossary/getNewRootProposals'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { buildRootIndex } from '~~/server/services/glossary/buildRootIndex'

export default defineEventHandler(async (event) => {
    // Glossary data changes only with a deploy; keep it in the browser for a few minutes.
    setResponseHeader(event, 'cache-control', 'private, max-age=600')
    return buildRootIndex(await getEntryIndex(), await getProposalIndex(), await getNewRootProposals())
})
