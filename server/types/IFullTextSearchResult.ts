import type { IVerbMetadataWithPreview } from '~~/types/IVerbMetadataWithPreview'

export interface IFullTextSearchResult {
    total: number
    roots: string[]
    verbMetadata: Record<string, IVerbMetadataWithPreview>
}
