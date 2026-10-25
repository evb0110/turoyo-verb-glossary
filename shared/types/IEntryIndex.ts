export interface IEntryIndex {
    id: string
    root: string
    homonym: number | null
    stems: Array<{ stem: string
        forms: string }>
    glossPreview: string
    exampleCount: number
    volume: string
    proposed?: boolean
}
