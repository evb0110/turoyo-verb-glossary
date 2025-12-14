interface IExample {
    text: string
    translations?: string[]
    references?: string[]
    notes?: string
}

interface IExamples {
    meaningNumber?: number
    items: IExample[]
    notes?: string
}

type TShape
    = | 'Preterit'
        | 'Preterit Intransitive'
        | 'Preterit Transitive'
        | 'ko-Preterit'
        | 'Preterit-wa'
        | 'Infectum'
        | 'Infectum-wa'
        | 'Imperativ'
        | 'Part act.'
        | 'Part. Pass.'
        | 'Infinitiv'
        | 'Action noun'
        | 'Nomen Actionis'
        | 'Nomen Patiens'
        | 'Nomen agentis'

interface IRow {
    shape: TShape
    examples: IExamples[]
    notes?: string
}

interface IMeaning {
    meaningNumber: number
    meaning: string
    notes?: string
}

type TStemNumber = 'I' | 'II' | 'III'

interface IStem {
    stemNumber: TStemNumber
    stemForms: string
    meanings?: IMeaning[]
    transitive: IRow[]
    detransitive?: IRow[]
    idiomaticPhrases?: IExample[]
    notes?: string
}

interface IEtymology {
    provenance?: string
    text: string
    notes?: string
}

interface IIdiom {
    text: string
    translation?: string
    notes?: string
}

export interface IEntry {
    lemma: string
    homonymNumber?: number
    etymology?: IEtymology
    stems?: IStem[]
    idioms?: IIdiom[]
    crossReference?: string
    uncertain?: boolean
    notes?: string
}
