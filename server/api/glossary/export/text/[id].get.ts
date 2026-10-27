import { getText } from '~~/server/repositories/glossary/getText'
import { buildTextDocument } from '~~/server/services/export/buildTextDocument'
import { exportContext } from '~~/server/utils/exportContext'
import { readExportFormat } from '~~/server/utils/readExportFormat'
import { sendDocument } from '~~/server/utils/sendDocument'

export default defineEventHandler(async (event) => {
    const format = readExportFormat(event)
    const text = await getText(getRouterParam(event, 'id', { decode: true }) || '')
    if (!text) throw createError({
        statusCode: 404,
        message: 'Text not found.',
    })
    return sendDocument(event, format, {
        key: `text:${text.id}`,
        revision: '',
        build: async () => buildTextDocument([text], null, exportContext(event)),
    })
})
