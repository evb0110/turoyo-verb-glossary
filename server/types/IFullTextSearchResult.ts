import type { IVerbMetadataWithPreview } from '~~/server/types/IVerbMetadataWithPreview'

export interface IFullTextSearchResult {
    total: number
    roots: string[]
    verbMetadata: Record<string, IVerbMetadataWithPreview>
}
