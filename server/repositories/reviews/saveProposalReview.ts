import { randomUUID } from 'node:crypto'
import { getTableColumns, sql } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'
import { proposalDecision } from '~~/server/db/schema'
import { devReviews } from '~~/server/repositories/reviews/devReviews'
import type { IProposalReview } from '#shared/types/IProposalReview'

export async function saveProposalReview(input: Omit<IProposalReview, 'id' | 'createdAt'>): Promise<IProposalReview> {
    const review = {
        ...input,
        id: randomUUID(),
        createdAt: new Date().toISOString(),
    }
    if (import.meta.dev && process.env.NUXT_DEV_AUTH_BYPASS === '1') {
        devReviews.events.unshift({
            ...review,
            previousReviewId: devReviews.current.get(input.proposalId)?.id || null,
            undoneReviewId: null,
        })
        devReviews.current.set(input.proposalId, review)
        return review
    }
    const edited = input.edited ? JSON.stringify(input.edited) : null
    // Wrap columns as SQL expressions because the FROM item is a set-returning function.
    // Keep Drizzle's column decoders, including timestamptz -> Date.
    const fields = Object.fromEntries(Object.entries(getTableColumns(proposalDecision))
        .map(([key, column]) => [key, sql`${column}`.mapWith(column)]))
    const rows = await getDatabase().select(fields).from(sql`
        public.save_proposal_decision(${review.id}, ${input.proposalId}, ${input.entryId},
            ${input.userId}, ${input.userName}, ${input.verdict}::public.proposal_verdict,
            ${input.comment}, ${edited}::jsonb) AS proposal_decision
    `)
    const saved = rows[0] as typeof proposalDecision.$inferSelect | undefined
    if (!saved) throw new Error('Review insert returned no record.')
    return {
        ...saved,
        createdAt: saved.createdAt.toISOString(),
    }
}
