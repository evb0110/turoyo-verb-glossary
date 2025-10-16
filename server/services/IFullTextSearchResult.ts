import type { IVerb } from '~/types/IVerb'
import type { IVerbMetadata } from '~/types/IVerbMetadata'
import type { IExcerpt } from '~/types/IExcerpt'

export interface IFullTextSearchResult {
    total: number
    roots: string[]
    verbPreviews: Record<string, { verb?: IVerb
        excerpts?: IExcerpt[] }>
    verbMetadata: Record<string, IVerbMetadata>
}
