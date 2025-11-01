export interface IExampleSegment {
    turoyo: string
    translations: string[]
    references: string[]
    notes?: string[]
}

export interface IExample {
    text?: string
    turoyo: string
    translations: string[]
    references: string[]
    tokens?: Array<import('~/types/IExampleToken').IExampleToken>
    segments?: IExampleSegment[]
}
