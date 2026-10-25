import type { IText } from '#shared/types/IText'

export function collectResearchNotes(texts: IText[]) {
    return texts.flatMap(text => (text.occurrences || [])
        .filter(occurrence => occurrence.rq.length > 0)
        .map((occurrence, n) => ({
            id: `${text.id}:${occurrence.v}:${n}`,
            textId: text.id,
            cite: `${text.cite}/${occurrence.v}`,
            title: text.title,
            occurrence,
        })))
}
