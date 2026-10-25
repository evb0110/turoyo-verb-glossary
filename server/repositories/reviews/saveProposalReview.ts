import { randomUUID } from 'node:crypto'
import { getDatabase } from '~~/server/db'
import { proposalReview } from '~~/server/db/schema'
import { devReviews } from '~~/server/repositories/reviews/devReviews'
import type { IProposalReview } from '#shared/types/IProposalReview'

export async function saveProposalReview(input: Omit<IProposalReview, 'id' | 'createdAt'>): Promise<IProposalReview> {
    const review = {
        ...input,
        id: randomUUID(),
        createdAt: new Date().toISOString(),
    }
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') {
        devReviews.unshift(review)
        return review
    }
    const [saved] = await getDatabase().insert(proposalReview).values({
        id: review.id,
        proposalId: input.proposalId,
        entryId: input.entryId,
        userId: input.userId,
        verdict: input.verdict,
        comment: input.comment,
    }).returning({ createdAt: proposalReview.createdAt })
    if (!saved) throw new Error('Review insert returned no record.')
    return {
        ...review,
        createdAt: saved.createdAt.toISOString(),
    }
}
