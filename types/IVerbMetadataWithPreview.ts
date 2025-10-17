import type { IVerbPreview } from '~~/server/services/extractVerbPreview'
import type { IExcerpt } from '~~/types/IExcerpt'
import type { IVerbMetadata } from '~~/types/IVerbMetadata'

export interface IVerbMetadataWithPreview extends IVerbMetadata {
    verbPreview?: IVerbPreview
    excerpts?: IExcerpt[]
}
