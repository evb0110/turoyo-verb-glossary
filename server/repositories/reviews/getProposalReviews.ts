import { desc } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { proposalDecision } from '~~/server/db/schema'
import { devReviews } from '~~/server/repositories/reviews/devReviews'
import type { IProposalReview } from '#shared/types/IProposalReview'

export async function getProposalReviews(): Promise<IProposalReview[]> {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') return [...devReviews.current.values()]
    const rows = await getDatabase().select().from(proposalDecision)
        .orderBy(desc(proposalDecision.createdAt), desc(proposalDecision.id))
    return rows.map(row => ({
        ...row,
        createdAt: row.createdAt.toISOString(),
    }))
}
