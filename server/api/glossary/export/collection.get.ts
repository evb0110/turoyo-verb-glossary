import { getText } from '~~/server/repositories/glossary/getText'
import { getTextIndex } from '~~/server/repositories/glossary/getTextIndex'
import { buildTextDocument } from '~~/server/services/export/buildTextDocument'
import { exportContext } from '~~/server/utils/exportContext'
import { readExportFormat } from '~~/server/utils/readExportFormat'
import { sendDocument } from '~~/server/utils/sendDocument'
import type { IText } from '#shared/types/IText'

// Every text of one collection (?collection=Jan BS), in the order of the texts list.
export default defineEventHandler(async (event) => {
    const format = readExportFormat(event)
    const collection = String(getQuery(event).collection || '')
    const rows = (await getTextIndex()).filter(row => row.collection === collection)
    if (!collection || !rows.length) throw createError({
        statusCode: 404,
        message: 'Collection not found.',
    })
    return sendDocument(event, format, {
        key: `collection:${collection}`,
        revision: '',
        build: async () => buildTextDocument(
            (await Promise.all(rows.map(row => getText(row.id)))).filter((text): text is IText => text !== null),
            collection,
            exportContext(event)
        ),
    })
})
