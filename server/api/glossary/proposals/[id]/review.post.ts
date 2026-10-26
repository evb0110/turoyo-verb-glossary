import { getProposal } from '~~/server/repositories/glossary/getProposal'
import { saveProposalReview } from '~~/server/repositories/reviews/saveProposalReview'
import { logUserActivity } from '~~/server/services/activity/logUserActivity'
import { requireApproved } from '~~/server/services/auth/requireApproved'
import type { IProposalEdit } from '#shared/types/IProposalEdit'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

export default defineEventHandler(async (event) => {
    const user = await requireApproved(event)
    const body = await readBody<{ verdict?: unknown
        comment?: unknown
        acceptWithChanges?: unknown
        edited?: unknown }>(event)
    if (!body || typeof body.verdict !== 'string' || !['accept', 'reject', 'discuss'].includes(body.verdict)) {
        throw createError({
            statusCode: 400,
            message: 'Choose accept, reject or discuss.',
        })
    }
    if (body.comment !== undefined && body.comment !== null && typeof body.comment !== 'string') {
        throw createError({
            statusCode: 400,
            message: 'Comment must be text.',
        })
    }
    const comment = typeof body.comment === 'string' ? body.comment.trim() : ''
    if (comment.length > 5000) throw createError({
        statusCode: 400,
        message: 'Comment is too long (maximum 5000).',
    })
    const proposal = await getProposal(getRouterParam(event, 'id', { decode: true }) || '')
    if (!proposal) throw createError({
        statusCode: 404,
        message: 'Proposal not found.',
    })
    if (body.acceptWithChanges !== undefined && typeof body.acceptWithChanges !== 'boolean')
        throw createError({
            statusCode: 400,
            message: 'Edited acceptance must be true or false.',
        })
    let edited: IProposalEdit | null = null
    if (body.acceptWithChanges === true) {
        if (body.verdict !== 'accept' || ['note', 'question'].includes(proposal.kind))
            throw createError({
                statusCode: 400,
                message: 'Only a suggested change can be accepted with changes.',
            })
        if (!body.edited || typeof body.edited !== 'object' || Array.isArray(body.edited))
            throw createError({
                statusCode: 400,
                message: 'Enter the edited wording before accepting.',
            })
        const fields = body.edited as Record<string, unknown>
        const hasTranslation = ['add-example', 'new-form', 'new-idiom'].includes(proposal.kind)
            || typeof proposal.data.translation === 'string'
        const hasHeadword = proposal.kind === 'new-idiom' && typeof proposal.data.headword === 'string'
        const allowed = ['text', ...(hasTranslation ? ['translation'] : []), ...(hasHeadword ? ['headword'] : [])]
        if (Object.keys(fields).some(key => !allowed.includes(key))
            || allowed.some(key => typeof fields[key] !== 'string'))
            throw createError({
                statusCode: 400,
                message: 'Use the text fields provided for this suggestion.',
            })
        const text = String(fields.text).trim()
        if (!text || text.length > 20000)
            throw createError({
                statusCode: 400,
                message: 'Edited wording is required (maximum 20000 characters).',
            })
        edited = { text }
        if (hasTranslation) {
            const translation = String(fields.translation).trim()
            if (translation.length > 20000)
                throw createError({
                    statusCode: 400,
                    message: 'Translation is too long (maximum 20000 characters).',
                })
            edited.translation = translation
        }
        if (hasHeadword) {
            const headword = String(fields.headword).trim()
            if (!headword || headword.length > 5000)
                throw createError({
                    statusCode: 400,
                    message: 'Idiom heading is required (maximum 5000 characters).',
                })
            edited.headword = headword
        }
    }
    else if (body.edited !== undefined && body.edited !== null)
        throw createError({
            statusCode: 400,
            message: 'Choose Save and accept to save edited wording.',
        })
    const review = await saveProposalReview({
        proposalId: proposal.id,
        entryId: proposal.entryId,
        userId: user.id,
        userName: user.name,
        verdict: body.verdict as TReviewVerdict,
        comment: comment || null,
        edited,
    })
    await logUserActivity(event, {
        eventType: 'view_verb',
        query: proposal.entryId,
        metadata: {
            action: 'proposal_review',
            proposalId: proposal.id,
            verdict: review.verdict,
            acceptedWithChanges: !!review.edited,
        },
    })
    setResponseHeader(event, 'Cache-Control', 'private, no-store')
    return review
})
