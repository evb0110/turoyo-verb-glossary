import { desc, eq } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { proposalReview, user } from '~~/server/db/schema'
import { devReviews } from '~~/server/repositories/reviews/devReviews'
import type { IProposalReview } from '#shared/types/IProposalReview'

export async function getProposalReviews(): Promise<IProposalReview[]> {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') return [...devReviews]
    const rows = await getDatabase().select({
        review: proposalReview,
        userName: user.name,
    })
        .from(proposalReview).innerJoin(user, eq(proposalReview.userId, user.id))
        .orderBy(desc(proposalReview.createdAt), desc(proposalReview.id))
    return rows.map(row => ({
        ...row.review,
        userName: row.userName,
        createdAt: row.review.createdAt.toISOString(),
    }))
}
