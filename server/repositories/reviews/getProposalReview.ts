import { eq } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { proposalDecision } from '~~/server/db/schema'
import { devReviews } from '~~/server/repositories/reviews/devReviews'
import type { IProposalReview } from '#shared/types/IProposalReview'

// The current decision on one proposal, or null when it is undecided.
export async function getProposalReview(proposalId: string): Promise<IProposalReview | null> {
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') return devReviews.current.get(proposalId) || null
    const [row] = await getDatabase().select().from(proposalDecision).where(eq(proposalDecision.proposalId, proposalId))
    return row
        ? {
                ...row,
                createdAt: row.createdAt.toISOString(),
            }
        : null
}
