import type { IStem } from '#shared/types/IStem'

interface ISenseRow {
    n: string
    key: string
    gloss: string
}

// One row per meaning number, in order. The Word text sometimes repeats a number (dry I numbers the
// meanings again inside an editorial note); the repeated glosses join the first row, so each example
// and suggestion with that number appears once.
export function glossarySenses(stem: IStem) {
    const rows: ISenseRow[] = []
    function add(row: ISenseRow) {
        const same = rows.find(item => item.key === row.key)
        if (same) same.gloss = `${same.gloss} ${row.gloss}`.trim()
        else rows.push(row)
    }
    for (const sense of stem.senses) add({
        n: sense.n,
        key: sense.n,
        gloss: sense.gloss,
    })
    for (const sense of stem.detransitiveSenses) add({
        n: sense.n,
        key: `D${sense.n}`,
        gloss: sense.gloss,
    })
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
