import { and, eq, sql } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { proposalReview } from '~~/server/db/schema'
import { devReviews } from '~~/server/repositories/reviews/devReviews'
import { ensureProposalReviewTable } from '~~/server/repositories/reviews/ensureProposalReviewTable'

export async function undoProposalReview(
    reviewId: string,
    proposalId: string,
    userId: string
): Promise<string | null> {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') {
        const latest = devReviews.find(item => item.proposalId === proposalId)
        if (!latest || latest.id !== reviewId || latest.userId !== userId)
            return null
        devReviews.splice(devReviews.indexOf(latest), 1)
        return reviewId
    }
    await ensureProposalReviewTable()
    const [removed] = await getDatabase()
        .delete(proposalReview)
        .where(
            and(
                eq(proposalReview.id, reviewId),
                eq(proposalReview.proposalId, proposalId),
                eq(proposalReview.userId, userId),
                sql`${proposalReview.id} = (SELECT id FROM proposal_review WHERE proposal_id = ${proposalId} ORDER BY created_at DESC, id DESC LIMIT 1)`
            )
        )
        .returning({ id: proposalReview.id })
    return removed?.id || null
}
