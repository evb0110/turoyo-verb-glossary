import type { IVerb } from '#shared/types/IVerb'

export interface IVerbDatabase {
    findByRoot(root: string): Promise<IVerb | null>
    findAll(): Promise<IVerb[]>
    searchByRoot(query: string): Promise<IVerb[]>
    getRoots(): Promise<string[]>
    count(): Promise<number>
    upsertVerb(verb: IVerb): Promise<void>
    upsertMany(verbs: IVerb[]): Promise<void>
    deleteAll(): Promise<void>
    close(): Promise<void>
}
