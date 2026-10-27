import { measureBlocks } from '~~/server/services/export/measureBlocks'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'
import type { TExportFormat } from '~~/server/types/export/TExportFormat'

// Expected file size in bytes, fitted to the whole glossary, two collections, a text, an entry and
// research notes (within about 10%). A PDF heading costs most: outline item, destination and structure element.
export function estimateSize(blocks: TDocBlock[], format: TExportFormat): number {
    const size = measureBlocks(blocks)
    return format === 'pdf'
        ? 50_000 + 0.9 * size.characters + 140 * size.paragraphs + 600 * size.headings + 580 * size.verses
        : 12_000 + 0.23 * size.characters + 15 * size.paragraphs + 55 * size.headings + 87 * size.verses
}
