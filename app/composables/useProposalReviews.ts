import type { IProposalEdit } from '#shared/types/IProposalEdit'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

// The read of the decisions in progress per app, shared by pages that load at the same time.
const reading = new WeakMap<object, Promise<void>>()

// The current team decision per proposal, keyed by proposal ID. The server sends one
// current row per proposal; the audit history is loaded separately per card.
export function useProposalReviews() {
    const decisions = useState<Record<string, IProposalReview>>('proposal-decisions', () => ({}))
    const loaded = useState('proposal-reviews-loaded', () => false)
    const error = useState('proposal-reviews-error', () => '')
    const pending = useState<string[]>('proposal-reviews-pending', () => [])
    // A counter bumped by every decision or undo here, and the count at each proposal's last change,
    // so a read that started earlier does not overwrite it.
    const changes = useState('proposal-reviews-changes', () => 0)
    const changedAt = useState<Record<string, number>>('proposal-reviews-changed-at', () => ({}))
    // Counts completed reads, so pages can react to decisions that arrived with one.
    const reads = useState('proposal-reviews-reads', () => 0)
    const request = useRequestFetch()
    const nuxtApp = useNuxtApp()
    const { user } = useAuth()
    function index(rows: IProposalReview[]) {
        return Object.fromEntries(rows.map(row => [row.proposalId, row]))
    }
    function changed(proposalId: string) {
        changes.value += 1
        changedAt.value[proposalId] = changes.value
    }
    function setDecision(proposalId: string, row: IProposalReview | null | undefined) {
        if (row) decisions.value[proposalId] = row
        else Reflect.deleteProperty(decisions.value, proposalId)
    }
    // Reads the team's decisions again each time a page needs them, so decisions other editors made
    // meanwhile appear. Hydration reuses the server's read. Once decisions are loaded, pages show them
    // at once and the read updates them when it returns.
    function load() {
        if (loaded.value && nuxtApp.isHydrating) return Promise.resolve()
        const running = reading.get(nuxtApp)
        if (running) return loaded.value ? Promise.resolve() : running
        const startedAt = changes.value
        const read = (async () => {
            try {
                const rows = index(await request<IProposalReview[]>('/api/glossary/reviews'))
                for (const [proposalId, at] of Object.entries(changedAt.value)) {
                    if (at <= startedAt) continue
                    const local = decisions.value[proposalId]
                    if (local) rows[proposalId] = local
                    else Reflect.deleteProperty(rows, proposalId)
                }
                decisions.value = rows
                loaded.value = true
                reads.value += 1
                // A message about a decision or undo made after this read began still stands.
                if (changes.value === startedAt) error.value = ''
            }
            catch {
                if (!loaded.value)
                    error.value = 'Earlier decisions could not be loaded. Please try again before reviewing.'
            }
            finally {
                reading.delete(nuxtApp)
            }
        })()
        reading.set(nuxtApp, read)
        return loaded.value ? Promise.resolve() : read
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
        changed(proposalId)
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
            changed(proposalId)
            decisions.value[proposalId] = saved
            return saved
        }
        catch {
            changed(proposalId)
            setDecision(proposalId, previous)
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
        // Marked from the start, so a read that began earlier neither overwrites this proposal nor
        // clears a message about this undo, even when the undo is refused.
        changed(item.proposalId)
        error.value = ''
        let result: { current?: IProposalReview | null }
        try {
            result = await $fetch(`/api/glossary/proposals/${item.proposalId}/review`, {
                method: 'DELETE',
                body: { reviewId: item.id },
            })
        }
        catch {
            // Also after a refusal, so a read that began while the undo was pending keeps this message.
            changed(item.proposalId)
            error.value
                = 'The decision could not be undone. It may have been changed by another editor. Reload to see the latest decision.'
            pending.value = pending.value.filter(id => id !== item.proposalId)
            return false
        }
        // The undo is saved. It may restore another editor's earlier decision, which the server sends
        // back; when it could not, only this proposal's row is read again.
        changed(item.proposalId)
        try {
            setDecision(item.proposalId, result.current !== undefined
                ? result.current
                : (await request<IProposalReview[]>('/api/glossary/reviews'))
                        .find(row => row.proposalId === item.proposalId))
        }
        catch {
            changed(item.proposalId)
            setDecision(item.proposalId, null)
            error.value = 'The decision was undone, but the decision now in force could not be loaded. Reload to see it.'
        }
        finally {
            pending.value = pending.value.filter(id => id !== item.proposalId)
        }
        return true
    }
    return {
        decisions,
        reads,
        error,
        pending,
        load,
        decision,
        status,
        review,
        undo,
    }
}
