#!/usr/bin/env node
import { readdir, readFile, writeFile, mkdir, stat, rm } from 'fs/promises'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const rootDir = join(__dirname, '..')

async function tryLoadJSON(path) {
  try {
    await stat(path)
    return JSON.parse(await readFile(path, 'utf-8'))
  } catch {
    return null
  }
}

async function buildAPI() {
  console.log('🔨 Building API data from source...')

  // Preferred: new v5 fully-segmented dataset
  const v5 = await tryLoadJSON(join(rootDir, 'data/verbs_final_v5.json'))

  // 1. Load all source files
  const sourceDir = join(rootDir, 'data/source/verbs')
  let allVerbs = []

  if (v5 && Array.isArray(v5.verbs) && v5.verbs.length > 0) {
    console.log(`✅ Using v5 dataset: ${v5.verbs.length} verbs`)
    allVerbs = v5.verbs
  } else {
    try {
      const files = await readdir(sourceDir)
      const jsonFiles = files.filter(f => f.endsWith('.json'))

      if (jsonFiles.length === 0) {
        // Fallback: if no source files, try to load from complete file
        console.log('⚠️  No source files found, loading from turoyo_verbs_complete.json...')
        const completeFile = join(rootDir, 'data/turoyo_verbs_complete.json')
        const data = JSON.parse(await readFile(completeFile, 'utf-8'))
        allVerbs = data.verbs
      } else {
        console.log(`📂 Loading ${jsonFiles.length} source files...`)
        for (const file of jsonFiles) {
          const data = JSON.parse(await readFile(join(sourceDir, file), 'utf-8'))
          if (data.verbs && Array.isArray(data.verbs)) {
            allVerbs.push(...data.verbs)
          }
        }
      }
    } catch (error) {
      console.log('⚠️  Source directory not found, loading from turoyo_verbs_complete.json...')
      const completeFile = join(rootDir, 'data/turoyo_verbs_complete.json')
      const data = JSON.parse(await readFile(completeFile, 'utf-8'))
      allVerbs = data.verbs
    }
  }

  console.log(`📚 Loaded ${allVerbs.length} verbs`)

  // 2. Create individual verb files
  const verbsDir = join(rootDir, 'data/api/verbs')
  await mkdir(verbsDir, { recursive: true })
  // Cleanup stale files
  try {
    const existing = await readdir(verbsDir)
    await Promise.all(existing.map(name => rm(join(verbsDir, name), { force: true })))
  } catch {}

  for (const verb of allVerbs) {
    const filename = join(verbsDir, `${verb.root}.json`)
    await writeFile(filename, JSON.stringify(verb, null, 2))
  }

  console.log(`✅ Created ${allVerbs.length} individual verb files`)

  // 3. Build index
  const index = {
    version: '1.0.0',
    total_verbs: allVerbs.length,
    last_updated: new Date().toISOString(),
    roots: allVerbs.map(v => {
      // Calculate example count
      let exampleCount = 0
      for (const stem of v.stems || []) {
        for (const examples of Object.values(stem.conjugations || {})) {
          exampleCount += examples.length
        }
      }

      // Get all forms
      const forms = []
      for (const stem of v.stems || []) {
        if (stem.forms && Array.isArray(stem.forms)) {
          forms.push(...stem.forms)
        }
      }

      return {
        root: v.root,
        etymology_source: v.etymology?.source || null,
        stems: (v.stems || []).map(s => s.stem),
        has_detransitive: (v.stems || []).some(s => s.stem === 'Detransitive'),
        cross_reference: v.cross_reference,
        example_count: exampleCount,
        forms: forms
      }
    })
  }

  await writeFile(join(rootDir, 'data/api/index.json'), JSON.stringify(index, null, 2))
  console.log('✅ Created index.json')

  // 4. Build search index
  const searchIndex = {
    turoyo_index: {},
    translation_index: {},
    etymology_index: {}
  }

  for (const verb of allVerbs) {
    // Index forms
    for (const stem of verb.stems || []) {
      for (const form of stem.forms || []) {
        if (!searchIndex.turoyo_index[form]) {
          searchIndex.turoyo_index[form] = []
        }
        if (!searchIndex.turoyo_index[form].includes(verb.root)) {
          searchIndex.turoyo_index[form].push(verb.root)
        }
      }

      // Index Turoyo examples and translations
      for (const [conjugationType, examples] of Object.entries(stem.conjugations || {})) {
        for (const ex of examples) {
          // Index Turoyo text
          if (ex.turoyo) {
            const words = ex.turoyo.split(/[\s\-.,;:!?()]+/).filter(w => w.length > 2)
            for (const word of words) {
              const cleanWord = word.replace(/[=\[\]()"<>]/g, '')
              // Only index words that:
              // - Are at least 3 chars long
              // - Don't contain numbers, slashes, underscores, or special markers
              // - Contain only valid Turoyo letters (including diacritics)
              const isValidTuroyoWord = /^[a-zʕṭḥṣčǧġšžḏṯʔāēīōūăĕĭŏŭ]+$/i.test(cleanWord)
              if (cleanWord.length > 2 && isValidTuroyoWord) {
                if (!searchIndex.turoyo_index[cleanWord]) {
                  searchIndex.turoyo_index[cleanWord] = []
                }
                if (!searchIndex.turoyo_index[cleanWord].includes(verb.root)) {
                  searchIndex.turoyo_index[cleanWord].push(verb.root)
                }
              }
            }
          }

          // Index translations
          if (ex.translations && Array.isArray(ex.translations)) {
            for (const translation of ex.translations) {
              const words = translation.split(/[\s\-.,;:!?()]+/).filter(w => w.length > 2)
              for (const word of words) {
                const cleanWord = word.toLowerCase()
                if (cleanWord.length > 2) {
                  if (!searchIndex.translation_index[cleanWord]) {
                    searchIndex.translation_index[cleanWord] = []
                  }
                  if (!searchIndex.translation_index[cleanWord].includes(verb.root)) {
                    searchIndex.translation_index[cleanWord].push(verb.root)
                  }
                }
              }
            }
          }
        }
      }
    }

    // Index etymology
    if (verb.etymology?.source) {
      const src = verb.etymology.source
      if (!searchIndex.etymology_index[src]) {
        searchIndex.etymology_index[src] = []
      }
      searchIndex.etymology_index[src].push(verb.root)
    }
  }

  await writeFile(join(rootDir, 'data/api/search.json'), JSON.stringify(searchIndex, null, 2))
  console.log('✅ Created search.json')

  // 5. Build statistics
  const stats = {
    total_verbs: allVerbs.length,
    total_stems: allVerbs.reduce((sum, v) => sum + (v.stems || []).length, 0),
    total_examples: 0,
    by_etymology: {},
    by_stem: {},
    by_letter: {}
  }

  for (const verb of allVerbs) {
    // Count examples
    for (const stem of verb.stems || []) {
      for (const examples of Object.values(stem.conjugations || {})) {
        stats.total_examples += examples.length
      }
    }

    // Etymology stats
    const src = verb.etymology?.source || 'Unknown'
    stats.by_etymology[src] = (stats.by_etymology[src] || 0) + 1

    // Stem stats
    for (const stem of verb.stems || []) {
      stats.by_stem[stem.stem] = (stats.by_stem[stem.stem] || 0) + 1
    }

    // Letter stats
    const letter = verb.root[0]
    stats.by_letter[letter] = (stats.by_letter[letter] || 0) + 1
  }

  await writeFile(join(rootDir, 'data/api/statistics.json'), JSON.stringify(stats, null, 2))
  console.log('✅ Created statistics.json')

  // 6. Build cross-references
  const crossRefs = {}
  for (const verb of allVerbs.filter(v => v.cross_reference)) {
    crossRefs[verb.root] = verb.cross_reference
  }

  await writeFile(join(rootDir, 'data/api/cross-refs.json'), JSON.stringify(crossRefs, null, 2))
  console.log('✅ Created cross-refs.json')

  console.log('\n🎉 Build complete!')
  console.log(`📊 Statistics:`)
  console.log(`   - Total verbs: ${stats.total_verbs}`)
  console.log(`   - Total stems: ${stats.total_stems}`)
  console.log(`   - Total examples: ${stats.total_examples}`)
  console.log(`   - Cross-references: ${Object.keys(crossRefs).length}`)
}

buildAPI().catch(error => {
  console.error('❌ Build failed:', error)
  process.exit(1)
})
