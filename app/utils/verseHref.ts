export function verseHref(textId: string, verse: number) {
    return `/texts/${encodeURIComponent(textId)}?v=${verse}`
}
