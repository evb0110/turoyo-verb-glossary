export interface ITextIndex {
    id: string
    cite: string
    title: string
    speakerPlace?: string | null
    collection: string
    file: string
    lang: 'GERMAN' | 'ENGLISH' | null
    verses: number
    translated: number
    words: number
    reading: 'unread' | 'partial' | 'read'
    occurrenceCount: number
}
