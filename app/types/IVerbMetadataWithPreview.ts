import type { IExcerpt } from '~/types/IExcerpt'
import type { IVerb } from '~/types/IVerb'
import type { IVerbMetadata } from '~/types/IVerbMetadata'

export interface IVerbMetadataWithPreview extends IVerbMetadata {
    verbPreview?: IVerb
    excerpts?: IExcerpt[]
}
