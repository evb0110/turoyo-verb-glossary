import type { IIdiom } from '#shared/types/IIdiom'
import type { IStem } from '#shared/types/IStem'

export interface IEntry {
    id: string
    root: string
    homonym: number | null
    head: string
    crossRefs: string[]
    notes: string[]
    stems: IStem[]
    idioms: IIdiom[]
    source: { volume: string
        order: number }
}
