import type { IExcerpt } from '#shared/types/IExcerpt'
import type { IVerb } from '#shared/types/IVerb'

export interface ITranslationSearchResponse {
    total: number
    roots: string[]
    verbPreviews: Record<string, {
        excerpts?: IExcerpt[]
        verb?: IVerb
    }>
}
