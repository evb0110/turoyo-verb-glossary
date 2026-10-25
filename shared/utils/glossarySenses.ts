import type { IStem } from '#shared/types/IStem'

export function glossarySenses(stem: IStem) {
    const rows = [
        ...stem.senses.map(sense => ({
            ...sense,
            key: sense.n,
        })),
        ...stem.detransitiveSenses.map(sense => ({
            ...sense,
            key: `D${sense.n}`,
        })),
    ]
    for (const box of stem.boxes)
        for (const example of box.examples) {
            const key = example.sense ? `${box.detransitive ? 'D' : ''}${example.sense}` : '?'
            if (!rows.some(row => row.key === key))
                rows.push({
                    n: key,
                    key,
                    gloss: key === '?' ? 'Unnumbered examples' : 'Sense not defined in the head',
                })
        }
    return rows
}
