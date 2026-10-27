import { getEntries } from '~~/server/repositories/glossary/getEntries'
import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getNewRootProposals } from '~~/server/repositories/glossary/getNewRootProposals'
import { getProposalIndex } from '~~/server/repositories/glossary/getProposalIndex'
import { getProposalDecisionExport } from '~~/server/repositories/reviews/getProposalDecisionExport'
import { buildDecisionsDocument } from '~~/server/services/export/buildDecisionsDocument'
import { buildRootIndex } from '~~/server/services/glossary/buildRootIndex'
import { exportContext } from '~~/server/utils/exportContext'
import { readExportFormat } from '~~/server/utils/readExportFormat'
import { sendDocument } from '~~/server/utils/sendDocument'

// Every current team decision for the editors, from the same data as the admin CSV/JSON download.
// Open to every approved user, who can already read each decision, reviewer, comment and edit on the site;
// it leaves out the reviewer IDs that the admin download carries. The decisions themselves are the revision:
// any saved, edited or undone decision makes a new document, and parts listed before it are refused.
export default defineEventHandler(async (event) => {
    const format = readExportFormat(event)
    const rows = await getProposalDecisionExport()
    return sendDocument(event, format, {
        key: 'decisions',
        revision: JSON.stringify(rows),
        build: async () => {
            const entryIds = [...new Set(rows.map(row => row.entryId))]
            const proposals = new Map((await Promise.all(entryIds.map(id => getEntryProposals(id))))
                .flat().map(proposal => [proposal.id, proposal]))
            const roots = buildRootIndex(await getEntryIndex(), await getProposalIndex(), await getNewRootProposals())
            return buildDecisionsDocument({
                rows,
                order: roots.map(root => root.id),
                entries: new Map((await getEntries(entryIds)).map(entry => [entry.id, entry])),
                proposals,
                context: exportContext(event),
            })
        },
    })
})
