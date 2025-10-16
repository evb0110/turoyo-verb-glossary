export interface IVerbStats {
    total_verbs: number
    total_stems: number
    total_examples: number
    stem_counts: Record<string, number>
    etymology_sources: Record<string, number>
    cross_references: number
    uncertain_entries: number
    homonyms: number
}
