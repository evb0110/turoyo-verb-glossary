import type { IAlignment } from '#shared/types/IAlignment'
import type { IOccurrence } from '#shared/types/IOccurrence'
import type { IVerse } from '#shared/types/IVerse'

export interface IText {
    id: string
    cite: string
    title: string
    speakerPlace?: string | null
    collection: string
    file: string
    lang: 'GERMAN' | 'ENGLISH' | null
    verses: IVerse[]
    reading?: 'unread' | 'partial' | 'read'
    occurrences?: IOccurrence[]
    alignment?: IAlignment[]
}
