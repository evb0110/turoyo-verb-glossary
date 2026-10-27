// An attachment header with an ASCII fallback name and the exact name as UTF-8 (RFC 6266 / 5987):
// turoyo-glossary-ʔbʕ.docx gives filename="turoyo-glossary-_b_.docx" and
// filename*=UTF-8''turoyo-glossary-%CA%94b%CA%95.docx
export function contentDisposition(fileName: string): string {
    const ascii = fileName.normalize('NFD').replace(/\p{M}/gu, '').replaceAll('ə', 'e')
        .replace(/[^\w.-]/gu, '_')
    const encoded = encodeURIComponent(fileName.normalize('NFC'))
        .replace(/['()*]/gu, char => `%${char.charCodeAt(0).toString(16).toUpperCase()}`)
    return `attachment; filename="${ascii}"; filename*=UTF-8''${encoded}`
}
