import type { IDocParagraph } from '~~/server/types/export/IDocParagraph'
import type { IExportContext } from '~~/server/types/export/IExportContext'
import { formatReviewDate } from '#shared/utils/formatReviewDate'

// The title block: title, scope, details and when and from which data the document was made.
export function exportFront(title: string, scope: string, details: string[], context: IExportContext): IDocParagraph[] {
    return [
        {
            type: 'paragraph',
            style: 'title',
            runs: [{ text: title }],
        },
        {
            type: 'paragraph',
            style: 'subtitle',
            runs: [{ text: scope }],
        },
        ...[
            ...details,
            `Glossary data: the Word volumes of ${context.snapshot || 'an unrecorded date'}, as parsed for the site.`,
            `Exported ${formatReviewDate(context.generated.toISOString())} from the Turoyo Verb Glossary site.`,
        ].map((text): IDocParagraph => ({
            type: 'paragraph',
            style: 'meta',
            runs: [{ text }],
        })),
    ]
}
