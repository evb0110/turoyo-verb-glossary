import { renderDocx } from '~~/server/services/export/renderDocx'
import { renderPdf } from '~~/server/services/export/renderPdf'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { IExportFonts } from '~~/server/types/export/IExportFonts'
import type { TExportFormat } from '~~/server/types/export/TExportFormat'

// Writes a document model in the requested format.
export async function renderDocument(
    doc: IExportDocument,
    format: TExportFormat,
    fonts: () => Promise<IExportFonts>
): Promise<Buffer> {
    return format === 'docx' ? await renderDocx(doc) : await renderPdf(doc, await fonts())
}
