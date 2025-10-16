import type { IVerb } from '~/types/IVerb'
import type { IVerbMetadata } from '~/types/IVerbMetadata'

export interface IRootsSearchResult {
    total: number
    roots: string[]
    verbPreviews: Record<string, { verb?: IVerb, excerpts?: never }>
    verbMetadata: Record<string, IVerbMetadata>
}
