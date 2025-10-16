export function makeGlobalRegex(regex: RegExp) {
    const flags = regex.flags.includes('g') ? regex.flags : `g${regex.flags}`
    return new RegExp(regex.source, flags)
}
