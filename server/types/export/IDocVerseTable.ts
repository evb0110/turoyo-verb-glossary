import type { IDocVerse } from '~~/server/types/export/IDocVerse'

// Verse number, Turoyo and translation side by side; `columns` labels the Turoyo and translation columns.
export interface IDocVerseTable {
    type: 'verses'
    columns: [string, string]
    rows: IDocVerse[]
}
