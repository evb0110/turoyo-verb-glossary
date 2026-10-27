// "1. ʔ, ʕ, b, č.docx" -> "Volume 1 (ʔ, ʕ, b, č)"
export function volumeLabel(volume: string): string {
    const match = /^(\d+)\.\s*(.*?)(?:\.docx)?$/u.exec(volume)
    return match ? `Volume ${match[1]} (${match[2]})` : volume.replace(/\.docx$/u, '')
}
