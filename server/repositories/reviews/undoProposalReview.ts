import { randomUUID } from 'node:crypto'
import { sql } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { devReviews } from '~~/server/repositories/reviews/devReviews'

export async function undoProposalReview(reviewId: string, proposalId: string, userId: string): Promise<string | null> {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') {
        const latest = devReviews.current.get(proposalId)
        if (!latest || latest.id !== reviewId || latest.userId !== userId) return null
        const event = devReviews.events.find(item => item.id === reviewId)
        const previous = devReviews.events.find(item => item.id === event?.previousReviewId)
        devReviews.events.unshift({
            ...latest,
            id: randomUUID(),
            verdict: null,
            edited: null,
            comment: null,
            previousReviewId: previous?.id || null,
            undoneReviewId: reviewId,
            createdAt: new Date().toISOString(),
        })
        if (previous?.verdict) devReviews.current.set(proposalId, {
            ...previous,
            verdict: previous.verdict,
        })
        else devReviews.current.delete(proposalId)
        return reviewId
    }
    const result = await getDatabase().execute(sql`
        SELECT public.undo_proposal_decision(${randomUUID()}, ${reviewId}, ${proposalId}, ${userId}) AS undone
    `)
    return result.rows[0]?.undone === true ? reviewId : null
}
