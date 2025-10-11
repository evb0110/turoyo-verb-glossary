// Type definitions for Turoyo Verb data structures

export interface Etymon {
    source: string
    source_root?: string
    reference?: string
    meaning?: string
    stem?: string // I, II, III, IV, Pa., Af., etc.
    raw?: string
}

export interface Etymology {
    etymons: Etymon[]
    relationship?: 'also' | 'or' | 'and'
}

export interface Example {
    turoyo: string
    translations: string[]
    references: string[]
}

export interface Stem {
    stem: string
    forms: string[]
    conjugations: {
        [key: string]: Example[]
    }
    // Optional fields from parser
    label_raw?: string
    label_gloss_tokens?: { italic: boolean, text: string }[]
}

export interface Verb {
    root: string
    etymology: Etymology | null
    cross_reference: string | null
    stems: Stem[]
    uncertain: boolean
    // Optional raw header HTML preserved verbatim
    lemma_header_raw?: string
}

export interface VerbIndexEntry {
    root: string
    etymology_sources: string[]
    stems: string[]
    has_detransitive: boolean
    cross_reference: string | null
    example_count: number
    forms: string[]
}

export interface VerbIndex {
    version: string
    total_verbs: number
    last_updated: string
    roots: VerbIndexEntry[]
}

export interface Statistics {
    total_verbs: number
    total_stems: number
    total_examples: number
    by_etymology: { [key: string]: number }
    by_stem: { [key: string]: number }
    by_letter: { [key: string]: number }
}

export interface CrossReferences {
    [key: string]: string
}
