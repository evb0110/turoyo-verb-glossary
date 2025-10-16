import { makeGlobalRegex } from '~~/server/utils/makeGlobalRegex'

export function findAllMatches(text: string, regex: RegExp): RegExpExecArray[] {
    const results: RegExpExecArray[] = []
    const globalRegex = makeGlobalRegex(regex)
    let match: RegExpExecArray | null

    while ((match = globalRegex.exec(text)) !== null) {
        results.push({
            ...match,
            index: match.index,
            input: match.input,
        } as RegExpExecArray)

        if (match[0].length === 0) {
            globalRegex.lastIndex += 1
        }
    }

    return results
}
