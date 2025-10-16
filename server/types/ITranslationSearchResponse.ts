import type { IExcerpt } from '~/types/IExcerpt'
import type { IVerb } from '~/types/IVerb'

export interface ITranslationSearchResponse {
    total: number
    roots: string[]
    verbPreviews: Record<string, {
        excerpts?: IExcerpt[]
        verb?: IVerb
    }>
}
