import { getAllTexts } from '~~/server/repositories/glossary/getAllTexts'
import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { buildResearchDocument } from '~~/server/services/export/buildResearchDocument'
import { collectResearchNotes } from '~~/server/services/glossary/collectResearchNotes'
import { filterResearchNotes } from '~~/server/services/glossary/filterResearchNotes'
import { exportContext } from '~~/server/utils/exportContext'
import { readExportFormat } from '~~/server/utils/readExportFormat'
import { sendDocument } from '~~/server/utils/sendDocument'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

// The research notes with the filters of /research: ?question=aspect and/or ?root=ʔb (roots beginning with it).
export default defineEventHandler(async (event) => {
    const format = readExportFormat(event)
    const query = getQuery(event)
    const question = String(query.question || '')
    const root = String(query.root || '').trim()
    const { matching } = filterResearchNotes(collectResearchNotes(await getAllTexts()), question, root)
    if (!matching.length) throw createError({
        statusCode: 404,
        message: 'No research notes match these filters.',
    })
    return sendDocument(event, format, {
        key: `research:${question}:${normalizeTuroyo(root)}`,
        revision: '',
        build: async () => buildResearchDocument({
            notes: matching,
            question,
            root,
            order: (await getEntryIndex()).map(row => row.id),
            context: exportContext(event),
        }),
    })
})
