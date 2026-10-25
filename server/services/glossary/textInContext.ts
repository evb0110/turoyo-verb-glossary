import type { IText } from '#shared/types/IText'

export function textInContext(text: IText, v: number): IText {
    return {
        ...text,
        verses: text.verses.filter(verse => Math.abs(verse.v - v) <= 3),
        occurrences: text.occurrences?.filter(item => Math.abs(item.v - v) <= 3),
        alignment: text.alignment?.filter(item => Math.abs(item.v - v) <= 3),
    }
}
