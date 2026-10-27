// A decision's day, such as "27 Oct 2026"; the decision history keeps the time as well.
export function formatDecisionDate(value: string) {
    return new Date(value).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        timeZone: 'UTC',
    })
}
