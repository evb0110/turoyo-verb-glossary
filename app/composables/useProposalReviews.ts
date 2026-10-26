import type { IProposalEdit } from '#shared/types/IProposalEdit'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

// The current team decision per proposal, keyed by proposal ID. The server sends one
// current row per proposal; the audit history is loaded separately per card.
export function useProposalReviews() {
    const decisions = useState<Record<string, IProposalReview>>('proposal-decisions', () => ({}))
    const loaded = useState('proposal-reviews-loaded', () => false)
    const error = useState('proposal-reviews-error', () => '')
    const pending = useState<string[]>('proposal-reviews-pending', () => [])
    const request = useRequestFetch()
    const { user } = useAuth()
    function index(rows: IProposalReview[]) {
        return Object.fromEntries(rows.map(row => [row.proposalId, row]))
    }
    async function load() {
        if (loaded.value) return
        try {
            decisions.value = index(await request<IProposalReview[]>('/api/glossary/reviews'))
            loaded.value = true
            error.value = ''
        }
        catch {
            error.value
                = 'Earlier decisions could not be loaded. Please try again before reviewing.'
        }
    }
    function decision(id: string): IProposalReview | null {
        return decisions.value[id] || null
    }
    function status(id: string) {
        const verdict = decisions.value[id]?.verdict
        return verdict === 'accept'
            ? 'accepted'
            : verdict === 'reject'
                ? 'rejected'
                : verdict || 'open'
    }
    async function review(
        proposalId: string,
        entryId: string,
        verdict: TReviewVerdict,
        comment = '',
        edited: IProposalEdit | null = null
    ) {
        if (pending.value.includes(proposalId) || !user.value) return false
        const previous = decisions.value[proposalId]
        decisions.value[proposalId] = {
            id: `pending:${proposalId}`,
            proposalId,
            entryId,
            verdict,
            edited,
            comment: comment || null,
            userId: user.value.id,
            userName: user.value.name,
            createdAt: new Date().toISOString(),
        }
        error.value = ''
        pending.value.push(proposalId)
        try {
            const saved = await $fetch<IProposalReview>(
                `/api/glossary/proposals/${proposalId}/review`,
                {
                    method: 'POST',
                    body: {
                        verdict,
                        comment,
                        edited,
                        acceptWithChanges: !!edited,
                    },
                }
            )
            decisions.value[proposalId] = saved
            return saved
        }
        catch {
            if (previous) decisions.value[proposalId] = previous
            else Reflect.deleteProperty(decisions.value, proposalId)
            error.value = 'Review was not saved. Please retry.'
            return false
        }
        finally {
            pending.value = pending.value.filter(id => id !== proposalId)
        }
    }
    async function undo(item: IProposalReview) {
        if (pending.value.includes(item.proposalId)) return false
        pending.value.push(item.proposalId)
        error.value = ''
        try {
            await $fetch(`/api/glossary/proposals/${item.proposalId}/review`, {
                method: 'DELETE',
                body: { reviewId: item.id },
            })
            // Undo may restore another editor's previous decision. Refresh only this proposal's
            // current row, so decisions saved meanwhile for other proposals stay in place.
            const current = (await request<IProposalReview[]>('/api/glossary/reviews'))
                .find(row => row.proposalId === item.proposalId)
            if (current) decisions.value[item.proposalId] = current
            else Reflect.deleteProperty(decisions.value, item.proposalId)
            return true
        }
        catch {
            error.value
                = 'The decision could not be undone. It may have been changed by another editor. Reload to see the latest decision.'
            return false
        }
        finally {
            pending.value = pending.value.filter(id => id !== item.proposalId)
        }
    }
    return {
        decisions,
        error,
        pending,
        load,
        decision,
        status,
        review,
        undo,
    }
}
