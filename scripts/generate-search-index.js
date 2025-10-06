#!/usr/bin/env node
/**
 * Generate lightweight search index from individual verb files
 * This runs at build time, so Vercel doesn't need to load all verbs on every request
 */
import { readdir, readFile, writeFile } from 'fs/promises'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const rootDir = join(__dirname, '..')

async function generateSearchIndex() {
    console.log('📝 Generating search index from verb files...')

    const verbsDir = join(rootDir, 'public', 'appdata', 'api', 'verbs')
    const files = await readdir(verbsDir)
    const verbFiles = files.filter(f => f.endsWith('.json'))

    console.log(`📚 Processing ${verbFiles.length} verb files...`)

    const index = []
    const crossRefs = {}

    for (const file of verbFiles) {
        try {
            const content = await readFile(join(verbsDir, file), 'utf-8')
            const verb = JSON.parse(content)

            // Build minimal index entry
            index.push({
                root: verb.root,
                etymology_sources: verb.etymology?.etymons?.map(e => e.source) || [],
                stems: verb.stems.map(s => s.stem).filter(Boolean),
                has_detransitive: verb.stems.some(s => s.stem === 'Detransitive'),
                cross_reference: verb.cross_reference,
                example_count: verb.stems.reduce((sum, s) =>
                    sum + Object.values(s.conjugations || {}).reduce((c, exs) => c + exs.length, 0), 0
                ),
                forms: verb.stems.flatMap(s => s.forms || [])
            })

            // Build cross-refs
            if (verb.cross_reference) {
                crossRefs[verb.root] = verb.cross_reference
            }
        }
        catch (err) {
            console.error(`Failed to process ${file}:`, err.message)
        }
    }

    // Write search index
    const searchIndexPath = join(rootDir, 'public', 'appdata', 'api', 'search-index.json')
    await writeFile(searchIndexPath, JSON.stringify({
        version: '1.0',
        total_verbs: index.length,
        last_updated: new Date().toISOString(),
        verbs: index
    }, null, 2))

    // Write cross-refs
    const crossRefsPath = join(rootDir, 'public', 'appdata', 'api', 'cross-refs.json')
    await writeFile(crossRefsPath, JSON.stringify(crossRefs, null, 2))

    // Generate statistics
    const stats = {
        total_verbs: index.length,
        total_stems: 0,
        total_examples: 0,
        by_etymology: {},
        by_stem: {},
        by_letter: {}
    }

    for (const verb of index) {
    // Count stems
        stats.total_stems += verb.stems?.length || 0

        // Count examples
        stats.total_examples += verb.example_count || 0

        // Count by etymology
        const sources = verb.etymology_sources || []
        for (const source of sources) {
            stats.by_etymology[source] = (stats.by_etymology[source] || 0) + 1
        }

        // Count by stem
        const stems = verb.stems || []
        for (const stemName of stems) {
            stats.by_stem[stemName] = (stats.by_stem[stemName] || 0) + 1
        }

        // Count by first letter
        const firstLetter = verb.root.charAt(0)
        stats.by_letter[firstLetter] = (stats.by_letter[firstLetter] || 0) + 1
    }

    // Write stats
    const statsPath = join(rootDir, 'public', 'appdata', 'api', 'stats.json')
    await writeFile(statsPath, JSON.stringify(stats, null, 2))

    console.log(`✅ Generated search-index.json (${index.length} verbs)`)
    console.log(`✅ Generated cross-refs.json (${Object.keys(crossRefs).length} cross-references)`)
    console.log(`✅ Generated stats.json (${stats.total_verbs} verbs, ${stats.total_stems} stems, ${stats.total_examples} examples)`)
}

generateSearchIndex().catch(console.error)
