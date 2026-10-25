export function inlineDiff(before: string, after: string) {
    const a = before.match(/\s+|[^\s]+/gu) || []
    const b = after.match(/\s+|[^\s]+/gu) || []
    // Keep unusually long source paragraphs bounded, while retaining their shared context.
    let left = 0
    while (left < a.length && left < b.length && a[left] === b[left]) left++
    let right = 0
    while (
        right < a.length - left
        && right < b.length - left
        && a[a.length - 1 - right] === b[b.length - 1 - right]
    )
        right++
    const old = a.slice(left, a.length - right)
    const next = b.slice(left, b.length - right)
    const parts: Array<{ text: string
        kind: 'same' | 'delete' | 'insert' }> = []
    if (left)
        parts.push({
            text: a.slice(0, left).join(''),
            kind: 'same',
        })
    if (old.length * next.length > 100000) {
        parts.push(
            {
                text: old.join(''),
                kind: 'delete',
            },
            {
                text: next.join(''),
                kind: 'insert',
            }
        )
    }
    else {
        const lengths = Array.from(
            { length: old.length + 1 },
            () => new Uint32Array(next.length + 1)
        )
        for (let i = old.length - 1; i >= 0; i--)
            for (let j = next.length - 1; j >= 0; j--)
                lengths[i]![j]
                    = old[i] === next[j]
                        ? lengths[i + 1]![j + 1]! + 1
                        : Math.max(lengths[i + 1]![j]!, lengths[i]![j + 1]!)
        let i = 0
        let j = 0
        while (i < old.length || j < next.length) {
            if (i < old.length && j < next.length && old[i] === next[j]) {
                parts.push({
                    text: old[i++]!,
                    kind: 'same',
                })
                j++
            }
            else if (
                i < old.length
                && (j === next.length || lengths[i + 1]![j]! >= lengths[i]![j + 1]!)
            )
                parts.push({
                    text: old[i++]!,
                    kind: 'delete',
                })
            else
                parts.push({
                    text: next[j++]!,
                    kind: 'insert',
                })
        }
    }
    if (right)
        parts.push({
            text: a.slice(a.length - right).join(''),
            kind: 'same',
        })
    return parts.reduce<typeof parts>((out, part) => {
        const last = out.at(-1)
        if (last?.kind === part.kind) last.text += part.text
        else out.push({ ...part })
        return out
    }, [])
}
