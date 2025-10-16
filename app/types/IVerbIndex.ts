import type { IVerbIndexEntry } from '~/types/IVerbIndexEntry'

export interface IVerbIndex {
    version: string
    total_verbs: number
    last_updated: string
    roots: IVerbIndexEntry[]
}
