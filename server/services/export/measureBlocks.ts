import type { TDocBlock } from '~~/server/types/export/TDocBlock'

// Counts what a document's size depends on: characters of text, headings, paragraphs and verse rows.
export function measureBlocks(blocks: TDocBlock[]) {
    let characters = 0
    let headings = 0
    let paragraphs = 0
    let verses = 0
    for (const block of blocks) {
        if (block.type === 'verses') {
            verses += block.rows.length
            for (const row of block.rows)
                characters += row.turoyo.length + row.translation.length + (row.note?.length || 0)
        }
        else {
            if (block.type === 'heading') headings++
            else paragraphs++
            for (const run of block.runs) characters += String(run.text ?? '').length
        }
    }
    return {
        characters,
        headings,
        paragraphs,
        verses,
    }
}
