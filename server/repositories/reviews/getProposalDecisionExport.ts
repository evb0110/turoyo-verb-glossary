import { getEntryIndex } from '~~/server/repositories/glossary/getEntryIndex'
import { getEntryProposals } from '~~/server/repositories/glossary/getEntryProposals'
import { getProposalReviews } from '~~/server/repositories/reviews/getProposalReviews'
import type { IProposalDecisionExport } from '#shared/types/IProposalDecisionExport'
import type { IProposalEdit } from '#shared/types/IProposalEdit'

export async function getProposalDecisionExport(): Promise<IProposalDecisionExport[]> {
    const roots = new Map((await getEntryIndex()).map(row => [row.id, row.root]))
    const reviews = await getProposalReviews()
    const entryIds = [...new Set(reviews.map(review => review.entryId))]
    const proposals = new Map((await Promise.all(entryIds.map(id => getEntryProposals(id))))
        .flat().map(proposal => [proposal.id, proposal]))
    return reviews.map((review) => {
        const proposal = proposals.get(review.proposalId)
        let machineText: IProposalEdit | null = null
        if (proposal) {
            machineText = {
                text: proposal.after
                    ?? String(proposal.data.turoyo ?? proposal.data.forms ?? proposal.data.gloss ?? proposal.summary),
            }
            if (['add-example', 'new-form', 'new-idiom'].includes(proposal.kind)
                || typeof proposal.data.translation === 'string')
                machineText.translation = String(proposal.data.translation ?? '')
            if (proposal.kind === 'new-idiom' && typeof proposal.data.headword === 'string')
                machineText.headword = proposal.data.headword
        }
        return {
            proposalId: review.proposalId,
            verb: roots.get(review.entryId) || review.entryId,
            kind: proposal?.kind || 'unavailable',
            citationTarget: {
                target: proposal?.target || {},
                citations: proposal?.evidence || [],
            },
            machineText,
            editedText: review.edited,
            verdict: review.verdict,
            comment: review.comment,
            reviewer: review.userName,
            reviewerId: review.userId,
            date: review.createdAt,
        }
    })
}
