import type { IExportContext } from '~~/server/types/export/IExportContext'
import type { H3Event } from 'h3'

export function exportContext(event: H3Event): IExportContext {
    return {
        generated: new Date(),
        snapshot: String(useRuntimeConfig(event).glossarySnapshot || ''),
    }
}
