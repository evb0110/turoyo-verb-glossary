// The readers tag the same question as "RQ-aspect" or "aspect"; both count as "aspect".
export function researchQuestion(tag: string): string {
    return tag.replace(/^RQ-/iu, '').toLowerCase()
}
