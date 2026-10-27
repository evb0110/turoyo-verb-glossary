import { createHash } from 'node:crypto'
import { getExportFonts } from '~~/server/repositories/export/getExportFonts'
import { planDocument } from '~~/server/services/export/planDocument'
import { renderDocument } from '~~/server/services/export/renderDocument'
import type { IExportDocument } from '~~/server/types/export/IExportDocument'
import type { TExportFormat } from '~~/server/types/export/TExportFormat'
import { cachedPlan } from '~~/server/utils/cachedPlan'
import { contentDisposition } from '~~/server/utils/contentDisposition'
import type { H3Event } from 'h3'

interface IExportScope {
    key: string // the validated scope, e.g. "glossary:ʔ:" or "entry:sym:suggestions"
    revision: string // what the document's content depends on beyond the deploy: '' for static data
    build: () => Promise<IExportDocument>
}

const TYPES: Record<TExportFormat, string> = {
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    pdf: 'application/pdf',
}

// ?part= is absent, or a whole number from 1; anything else is refused before any work is done.
function readPart(event: H3Event) {
    const value = getQuery(event).part
    if (value === undefined || value === '') return 0
    if (typeof value !== 'string' || !/^[1-9]\d{0,3}$/u.test(value))
        throw createError({
            statusCode: 400,
            message: 'Choose a part by its number.',
        })
    return Number(value)
}

// Sends a document as a download. One too large for a single response answers 300 Multiple Choices with its
// revision and parts; each part is then requested with &part=N&rev=…, and a part of an older revision (the
// decisions changed, or a new deploy) answers 409, so parts of different revisions are never mixed.
export async function sendDocument(event: H3Event, format: TExportFormat, scope: IExportScope) {
    const part = readPart(event)
    const revision = createHash('sha1')
        .update(`${useRuntimeConfig(event).app.buildId}\n${scope.revision}`).digest('hex').slice(0, 12)
    setResponseHeader(event, 'Cache-Control', 'private, no-store')
    if (part && getQuery(event).rev !== revision)
        throw createError({
            statusCode: 409,
            message: 'The document has changed since its parts were listed. List the parts again.',
        })
    const plan = await cachedPlan(`${scope.key}|${format}|${revision}`, async () => {
        const started = performance.now()
        const write = (doc: IExportDocument) => renderDocument(doc, format, getExportFonts)
        const parts = await planDocument(await scope.build(), format, write)
        return {
            revision,
            parts,
            milliseconds: Math.round(performance.now() - started),
        }
    })
    if (!part && plan.parts.length > 1) {
        setResponseStatus(event, 300)
        return {
            revision,
            parts: plan.parts.map(item => ({
                part: item.part,
                label: item.label,
                bytes: item.bytes.length,
            })),
        }
    }
    const file = plan.parts[(part || 1) - 1]
    if (!file) throw createError({
        statusCode: 400,
        message: 'There is no such part.',
    })
    setResponseHeaders(event, {
        'Content-Type': TYPES[format],
        'Content-Disposition': contentDisposition(file.fileName),
        'Content-Length': String(file.bytes.length),
        'Server-Timing': `plan;dur=${plan.milliseconds}`,
        'X-Content-Type-Options': 'nosniff',
    })
    return file.bytes
}
