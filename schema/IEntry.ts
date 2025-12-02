interface IExample {
    text: string
    translation?: string
    references?: string[]
}

interface IExamples {
    meaningNumber?: number
    items: IExample[]
}

type TShape = 'Preterit'
    | 'Infectum'
    | 'Infectum-wa'
    | 'Imperativ'
    | 'Preterit-wa'
    | 'Action noun'

type TRow = {
    shape: TShape
    examples: IExamples[]
}

interface IMeaning {
    meaningNumber: number
    meaning: string
}

type TStemNumber = 'I' | 'II' | 'III'

interface IStem {
    stemNumber: TStemNumber
    stemForms: string // qayəm/qoyəm
    meanings?: IMeaning[]
    transitive: TRow[] // as opposed to detransitive
    detransitive?: TRow[]
    idiomaticPhrases?: IExample[]
}

interface IEtymology {
    provenance: string // Arab
    source: string // qfz
    references: string[] // Wehr 1046-1047
    meaning: string // springen
}

interface IEntry {
    lemma: string // qbz
    etymologies?: IEtymology[]
    stems?: IStem[]
    notes: string
}
