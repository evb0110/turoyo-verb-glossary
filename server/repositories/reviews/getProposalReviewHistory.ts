import { desc, eq } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { proposalReviewEvent } from '~~/server/db/schema'
import { devReviews } from '~~/server/repositories/reviews/devReviews'
import type { IProposalReviewEvent } from '#shared/types/IProposalReviewEvent'

export async function getProposalReviewHistory(proposalId: string): Promise<IProposalReviewEvent[]> {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1')
        return devReviews.events.filter(item => item.proposalId === proposalId).slice(0, 100)
    const rows = await getDatabase().select().from(proposalReviewEvent)
        .where(eq(proposalReviewEvent.proposalId, proposalId))
        .orderBy(desc(proposalReviewEvent.createdAt), desc(proposalReviewEvent.id)).limit(100)
    return rows.map(row => ({
        ...row,
        createdAt: row.createdAt.toISOString(),
    }))
}
