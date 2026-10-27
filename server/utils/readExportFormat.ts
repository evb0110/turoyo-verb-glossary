import type { TExportFormat } from '~~/server/types/export/TExportFormat'
import type { H3Event } from 'h3'

export function readExportFormat(event: H3Event): TExportFormat {
    const format = getQuery(event).format
    if (format !== 'docx' && format !== 'pdf')
        throw createError({
            statusCode: 400,
            message: 'Choose format=docx or format=pdf.',
        })
    return format
}
