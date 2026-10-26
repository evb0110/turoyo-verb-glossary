export function formatReviewDate(value: string) {
    return `${new Date(value).toLocaleString('en-GB', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'UTC',
    })} UTC`
}
