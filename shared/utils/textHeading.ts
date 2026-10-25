export function textHeading(title: string, cite: string) {
    const prefix = /^([^\s_]+_[^\s_]+)(?:\s+|$)/u.exec(title)
    return {
        title: prefix ? title.slice(prefix[0].length).trim() || `Text ${cite}` : title,
        speakerPlace: prefix?.[1] || null,
    }
}
