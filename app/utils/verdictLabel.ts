import type { TReviewVerdict } from '#shared/types/TReviewVerdict'

export function verdictLabel(verdict: TReviewVerdict, question: boolean, edited = false) {
    if (verdict === 'accept') return question ? 'Noted' : edited ? 'Accepted with changes' : 'Accepted'
    if (verdict === 'reject') return question ? 'Dismissed' : 'Rejected'
    return question ? 'Discuss later' : 'Decide later'
}
