export function idiomTokens(raw: string, textIds: ReadonlySet<string>) {
    const tokens: Array<{
        text: string
        kind: 'headword' | 'turoyo' | 'translation' | 'annotation' | 'ref'
        textId?: string
        verse?: number
    }> = []
    const firstQuote = raw.search(/[‘ʻ“„']/u)
    const headEnd = firstQuote < 0 ? 0 : firstQuote
    if (headEnd)
        tokens.push({
            text: raw.slice(0, headEnd),
            kind: 'headword',
        })
    const content = raw.slice(headEnd)
    const pattern
        = /[‘ʻ“„'][^’ʼ”']*[’ʼ”']|\([^)]*\)|\[[^\]]*\]|\bJL\s+\d+\.\d+\.\d+|\b\d+\/\d+(?:[-–]\d+)?|\b\d{3,4}\b/giu
    let position = 0
    for (const match of content.matchAll(pattern)) {
        if (match.index > position)
            tokens.push({
                text: content.slice(position, match.index),
                kind: 'turoyo',
            })
        const text = match[0]
        const jl = /^JL\s+(\d+)\.(\d+)\.(\d+)$/iu.exec(text)
        const ritter = /^(\d+)\/(\d+)/u.exec(text)
        const textId = jl
            ? `JL${jl[1]!.padStart(2, '0')}.${jl[2]!.padStart(2, '0')}`
            : ritter
                ? `R${ritter[1]!.padStart(3, '0')}`
                : null
        if (textId && textIds.has(textId))
            tokens.push({
                text,
                kind: 'ref',
                textId,
                verse: Number(jl ? jl[3] : ritter![2]),
            })
        else
            tokens.push({
                text,
                kind: /^[‘ʻ“„']/u.test(text) ? 'translation' : 'annotation',
            })
        position = match.index + text.length
    }
    if (position < content.length)
        tokens.push({
            text: content.slice(position),
            kind: 'turoyo',
        })
    return tokens
}
