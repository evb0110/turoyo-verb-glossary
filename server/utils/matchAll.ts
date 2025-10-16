import { makeGlobalRegex } from '~~/server/utils/makeGlobalRegex'

export function* matchAll(text: string, regex: RegExp): Generator<RegExpExecArray> {
    const globalRegex = makeGlobalRegex(regex)
    let match: RegExpExecArray | null

    while ((match = globalRegex.exec(text)) !== null) {
        yield match

        if (match[0].length === 0) {
            globalRegex.lastIndex += 1
        }
    }
}
