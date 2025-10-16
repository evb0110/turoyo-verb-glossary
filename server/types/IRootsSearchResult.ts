import type { IVerbMetadataWithPreview } from '~~/server/types/IVerbMetadataWithPreview'

export interface IRootsSearchResult {
    total: number
    roots: string[]
    verbMetadata: Record<string, IVerbMetadataWithPreview>
}
