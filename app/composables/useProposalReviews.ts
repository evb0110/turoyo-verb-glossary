import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

export function useProposalReviews() {
    const reviews = useState<IProposalReview[]>('proposal-reviews', () => [])
    const loaded = useState('proposal-reviews-loaded', () => false)
    const error = useState('proposal-reviews-error', () => '')
    const pending = useState<string[]>('proposal-reviews-pending', () => [])
    const request = useRequestFetch()
    const { user } = useAuth()
    async function load() {
        if (loaded.value) return
        try {
            reviews.value = await request<IProposalReview[]>('/api/glossary/reviews')
            loaded.value = true
            error.value = ''
        }
        catch {
            error.value
                = 'Earlier decisions could not be loaded. Please try again before reviewing.'
        }
    }
    function history(id: string) {
        return reviews.value.filter(review => review.proposalId === id)
    }
    function status(id: string) {
        const verdict = history(id)[0]?.verdict
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
        comment = ''
    ) {
        if (pending.value.includes(proposalId) || !user.value) return false
        const optimistic: IProposalReview = {
            id: `pending:${proposalId}`,
            proposalId,
            entryId,
            verdict,
            comment: comment || null,
            userId: user.value.id,
            userName: user.value.name,
            createdAt: new Date().toISOString(),
        }
        error.value = ''
        reviews.value.unshift(optimistic)
        pending.value.push(proposalId)
        try {
            const saved = await $fetch<IProposalReview>(
                `/api/glossary/proposals/${proposalId}/review`,
                {
                    method: 'POST',
                    body: {
                        verdict,
                        comment,
                    },
                }
            )
            reviews.value = reviews.value.map(item =>
                item.id === optimistic.id ? saved : item
            )
            return saved
        }
        catch {
            reviews.value = reviews.value.filter(item => item.id !== optimistic.id)
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
            reviews.value = reviews.value.filter(review => review.id !== item.id)
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
        reviews,
        error,
        pending,
        load,
        history,
        status,
        review,
        undo,
    }
}
