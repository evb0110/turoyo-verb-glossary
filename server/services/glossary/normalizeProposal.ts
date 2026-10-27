import type { IProposal } from '#shared/types/IProposal'
import { plainValue } from '#shared/utils/plainValue'

// A few machine proposals carry a list or an object as `before`/`after` where the data contract has text;
// the entry page's diff failed on them (HTTP 500 for ḥyl and nfq). They are read as text.
export function normalizeProposal(proposal: IProposal): IProposal {
    const odd = (value: unknown) => value !== null && typeof value !== 'string'
    if (!odd(proposal.before) && !odd(proposal.after)) return proposal
    return {
        ...proposal,
        before: odd(proposal.before) ? plainValue(proposal.before) : proposal.before,
        after: odd(proposal.after) ? plainValue(proposal.after) : proposal.after,
    }
}
