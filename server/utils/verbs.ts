import statsData from '../../public/appdata/api/stats.json'

export interface Verb {
    root: string
    etymology: {
        etymons: Array<{
            source: string
            source_root?: string
            reference?: string
            meaning?: string
            notes?: string
            stem?: string
            raw?: string
        }>
        relationship?: 'also' | 'or' | 'and'
    } | null
    cross_reference: string | null
    stems: Array<{
        stem?: string
        forms: string[]
        conjugations: Record<string, Array<{
            turoyo: string
            translations: string[]
            references: string[]
        }>>
        label_raw?: string
        label_gloss_tokens?: Array<{ italic: boolean, text: string }>
    }>
    uncertain: boolean
    lemma_header_raw?: string
    lemma_header_tokens?: Array<{ italic: boolean, text: string }>
}

export function getStatistics() {
    return statsData
}
