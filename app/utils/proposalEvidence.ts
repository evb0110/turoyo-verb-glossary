import type { IExample } from '#shared/types/IExample'
import type { IProposal } from '#shared/types/IProposal'

// Every verse a suggestion rests on: its cited evidence, the example it changes and, for
// reference fixes, both the current and the suggested reference.
export function proposalEvidence(proposal: IProposal, example: IExample | null) {
    const rows: Array<{ textId: string
        v: number
        cite: string
        label: string }> = []
    function add(textId: string, v: number, cite: string, label: string) {
        if (!rows.some(item => item.textId === textId && item.v === v))
            rows.push({
                textId,
                v,
                cite,
                label,
            })
    }
    function parse(text: string, label: string) {
        for (const match of text.matchAll(
            /(?<![\p{L}\d.][ \u00A0]?)(?:R)?(\d{1,3})\/(\d+)(?:[-–](\d+))?/gu
        )) {
            const end = Math.min(Number(match[3] || match[2]), Number(match[2]) + 8)
            for (let v = Number(match[2]); v <= end; v++)
                add(`R${match[1]!.padStart(3, '0')}`, v, `${Number(match[1])}/${v}`, label)
        }
        for (const match of text.matchAll(/JL\s*(\d+)\.(\d+)\.(\d+)/gu))
            add(
                `JL${match[1]!.padStart(2, '0')}.${match[2]!.padStart(2, '0')}`,
                Number(match[3]),
                match[0],
                label
            )
    }
    if (proposal.kind === 'fix-citation') parse(proposal.after || '', 'Suggested reference')
    for (const ref of proposal.evidence) add(ref.textId, ref.v, ref.cite, 'Cited passage')
    for (const ref of example?.refs || [])
        if (ref.textId && ref.verse !== null)
            add(
                ref.textId,
                ref.verse,
                ref.raw,
                proposal.kind === 'fix-citation' ? 'Current reference' : 'Example in the text'
            )
    if (proposal.kind === 'fix-citation') parse(proposal.before || '', 'Current reference')
    // The bundle already resolves an addition's reference into evidence; parse it only as a fallback.
    if (!proposal.evidence.length)
        for (const value of [proposal.data.ref, proposal.data.reference])
            if (typeof value === 'string') parse(value, 'Source of the suggested addition')
    return rows
}
