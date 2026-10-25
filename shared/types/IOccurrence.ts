export interface IOccurrence {
    v: number
    form: string
    entryId: string | null
    root: string
    stem: string
    detransitive: boolean
    box: string
    sense: string
    senseFit: 'exact' | 'stretched' | 'none'
    meaning: string
    arguments: string
    observations: string | null
    note: string | null
    newSenseGloss: string | null
    newSenseType: string | null
    rq: string[]
    decision: 'add' | 'no-add'
    criterion: string
    proposalIds: string[]
}
