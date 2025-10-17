import type { IVerbMetadataWithPreview } from '~~/types/IVerbMetadataWithPreview'

export interface IRootsSearchResult {
    total: number
    roots: string[]
    verbMetadata: Record<string, IVerbMetadataWithPreview>
}
