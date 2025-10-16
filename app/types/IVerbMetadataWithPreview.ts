import type { IExcerpt } from '~/types/IExcerpt'
import type { IVerbMetadata } from '~/types/IVerbMetadata'
import type { IVerbPreview } from '~~/server/services/extractVerbPreview'

export interface IVerbMetadataWithPreview extends IVerbMetadata {
    verbPreview?: IVerbPreview
    excerpts?: IExcerpt[]
}
