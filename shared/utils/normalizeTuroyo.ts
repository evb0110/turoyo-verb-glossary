export function normalizeTuroyo(value: string): string {
    const keep = new Set(['\u0323', '\u0331', '\u030c', '\u0307'])
    return [...value.toLowerCase().normalize('NFD')]
        .filter(char => !/\p{M}/u.test(char) || keep.has(char))
        .join('').normalize('NFC').replace(/[=\-‐+‿’ʼ'`´]/gu, '')
}
