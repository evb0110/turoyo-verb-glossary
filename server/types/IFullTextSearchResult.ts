import type { IVerbMetadataWithPreview } from '#shared/types/IVerbMetadataWithPreview'

export interface IFullTextSearchResult {
    total: number
    roots: string[]
    verbMetadata: Record<string, IVerbMetadataWithPreview>
}
