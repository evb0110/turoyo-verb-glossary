import type { IVerbMetadataWithPreview } from '#shared/types/IVerbMetadataWithPreview'

export interface IRootsSearchResult {
    total: number
    roots: string[]
    verbMetadata: Record<string, IVerbMetadataWithPreview>
}
