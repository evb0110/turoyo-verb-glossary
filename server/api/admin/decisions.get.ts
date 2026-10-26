import { getProposalDecisionExport } from '~~/server/repositories/reviews/getProposalDecisionExport'
import { requireApproved } from '~~/server/services/auth/requireApproved'

export default defineEventHandler(async (event) => {
    const user = await requireApproved(event)
    if (user.role !== 'admin') throw createError({
        statusCode: 403,
        message: 'Admin access required.',
    })
    const format = getQuery(event).format || 'json'
    if (format !== 'csv' && format !== 'json')
        throw createError({
            statusCode: 400,
            message: 'Choose CSV or JSON.',
        })
    const decisions = await getProposalDecisionExport()
    setResponseHeader(event, 'Cache-Control', 'private, no-store')
    setResponseHeader(event, 'Content-Disposition', `attachment; filename="glossary-decisions.${format}"`)
    if (format === 'json') {
        setResponseHeader(event, 'Content-Type', 'application/json; charset=utf-8')
        return JSON.stringify(decisions, null, 2)
    }
    setResponseHeader(event, 'Content-Type', 'text/csv; charset=utf-8')
    const columns = [
        'proposalId', 'verb', 'kind', 'citationTarget', 'machineText', 'editedText',
        'verdict', 'comment', 'reviewer', 'reviewerId', 'date',
    ] as const
    function cell(value: unknown) {
        const text = value === null ? '' : typeof value === 'object' ? JSON.stringify(value) : String(value)
        // Prevent spreadsheet formulas while preserving exact source text in the JSON export.
        const safe = /^[\s]*[=+\-@]/u.test(text) ? `'${text}` : text
        return `"${safe.replaceAll('"', '""')}"`
    }
    return '\uFEFF' + [columns.join(','), ...decisions.map(row => columns.map(key => cell(row[key])).join(','))]
        .join('\r\n') + '\r\n'
})
