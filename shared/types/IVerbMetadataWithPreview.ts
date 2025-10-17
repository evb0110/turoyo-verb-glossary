import type { IVerbPreview } from '~~/server/services/extractVerbPreview'
import type { IExcerpt } from '#shared/types/IExcerpt'
import type { IVerbMetadata } from '#shared/types/IVerbMetadata'

export interface IVerbMetadataWithPreview extends IVerbMetadata {
    verbPreview?: IVerbPreview
    excerpts?: IExcerpt[]
}
