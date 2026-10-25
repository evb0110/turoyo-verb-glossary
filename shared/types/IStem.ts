import type { IBox } from '#shared/types/IBox'
import type { ISense } from '#shared/types/ISense'

export interface IStem {
    id: string
    stem: string
    forms: string
    senses: ISense[]
    sensesRaw: string
    detransitiveSenses: ISense[]
    detransitiveSensesRaw: string | null
    boxes: IBox[]
    notes: string[]
}
