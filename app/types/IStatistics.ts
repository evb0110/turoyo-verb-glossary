export interface IStatistics {
    total_verbs: number
    total_stems: number
    total_examples: number
    by_etymology: { [key: string]: number }
    by_stem: { [key: string]: number }
    by_letter: { [key: string]: number }
}
