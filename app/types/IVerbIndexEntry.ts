export interface IVerbIndexEntry {
    root: string
    etymology_sources: string[]
    stems: string[]
    has_detransitive: boolean
    cross_reference: string | null
    example_count: number
    forms: string[]
}
