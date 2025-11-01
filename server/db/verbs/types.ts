export interface IEtymology {
    language?: string
    meaning?: string
    relationships?: Array<{
        type: string
        root: string
        notes?: string
    }>
    notes?: string
}

export interface IExample {
    text: string
    turoyo: string
    translations: string[]
    references: string[]
}

export interface IStem {
    stem: string
    forms: string[]
    conjugations: Record<string, IExample[]>
}

export interface IVerbRow {
    root: string
    etymology: IEtymology | null
    stems: IStem[]
    idioms: string[] | null
    createdAt: Date | null
}
