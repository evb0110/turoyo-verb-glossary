# Turoyo Verb Glossary - Data Architecture

## Design Goals

1. **GitHub-friendly**: Easy PR reviews, clear diffs, linguist-editable
2. **Performance**: Fast loading in Nuxt app, lazy loading support
3. **Programmatic access**: REST-like API structure
4. **Maintainability**: Source of truth → built artifacts

---

## Directory Structure

```
turoyo-verb-glossary/
├── data/
│   ├── source/              # Source of truth (linguists edit here)
│   │   ├── verbs/
│   │   │   ├── ʔ.json      # 18 verbs starting with ʔ
│   │   │   ├── ʕ.json      # ~150 verbs starting with ʕ
│   │   │   ├── b.json      # ~80 verbs starting with b
│   │   │   ├── č.json
│   │   │   ├── d.json
│   │   │   └── ... (28 files, one per letter)
│   │   └── metadata.json    # Parser version, statistics, etc.
│   │
│   └── api/                 # Built artifacts (for Nuxt app)
│       ├── verbs/
│       │   ├── ʔbʕ.json    # Individual verb files (1,240 files)
│       │   ├── ʔdb.json
│       │   └── ...
│       ├── index.json       # Lightweight index: all roots + basic info
│       ├── search.json      # Optimized search index
│       ├── statistics.json  # Pre-computed statistics
│       └── cross-refs.json  # Cross-reference mappings
│
├── scripts/
│   ├── build-api.js         # Transform source → api
│   ├── validate.js          # Validate data integrity
│   └── stats.js             # Generate statistics
│
└── .github/
    └── workflows/
        └── build-data.yml   # Auto-build on PR merge
```

---

## Source Data Format (for Linguists)

### `data/source/verbs/{letter}.json`

```json
{
  "letter": "ʔ",
  "verbs": [
    {
      "root": "ʔbʕ",
      "etymology": {
        "source": "MA",
        "source_root": "bʕy",
        "reference": "SL 169",
        "meaning": "to strive after, pursue, desire"
      },
      "cross_reference": null,
      "stems": [
        {
          "binyan": "I",
          "forms": ["abəʕ", "obəʕ"],
          "conjugations": {
            "Preterit Intransitive": [
              {
                "turoyo": "mʔamalle, húle-le u=mede d-abəʕ",
                "translations": ["er befahl, ihm zu geben, was er wollte"],
                "references": ["731; 24/51"]
              }
            ]
          }
        }
      ],
      "uncertain": false
    }
  ]
}
```

**Benefits**:
- ✅ One file per letter = manageable PR diffs
- ✅ Complete verb entries in one place
- ✅ Easy to search and edit with text editor
- ✅ Git-friendly (clear conflict resolution)

---

## API Data Format (for Nuxt App)

### `data/api/index.json` (Lightweight, ~100KB)

```json
{
  "version": "1.0.0",
  "total_verbs": 1240,
  "last_updated": "2025-10-02T10:42:00Z",
  "roots": [
    {
      "root": "ʔbʕ",
      "etymology_source": "MA",
      "binyanim": ["I"],
      "has_detransitive": false,
      "cross_reference": null,
      "example_count": 12,
      "forms": ["abəʕ", "obəʕ"]
    },
    {
      "root": "ʕbd",
      "etymology_source": "Arab.",
      "binyanim": ["I"],
      "has_detransitive": false,
      "cross_reference": null,
      "example_count": 3,
      "forms": ["ʕbədle", "ʕobəd"]
    }
  ]
}
```

**Usage in Nuxt**:
```js
// Load once on app init
const index = await $fetch('/data/api/index.json')
// Show autocomplete, browse mode, statistics
```

---

### `data/api/verbs/{root}.json` (Individual files, 2-5KB each)

```json
{
  "root": "ʔbʕ",
  "etymology": {
    "source": "MA",
    "source_root": "bʕy",
    "reference": "SL 169",
    "meaning": "to strive after, pursue, desire; to request; to seek; to need, require"
  },
  "cross_reference": null,
  "stems": [
    {
      "binyan": "I",
      "forms": ["abəʕ", "obəʕ"],
      "conjugations": {
        "Preterit Intransitive": [
          {
            "turoyo": "mʔamalle, húle-le u=mede d-abəʕ, lirat dahwo w i=səstayḏe",
            "translations": ["er befahl, ihm zu geben, was er wollte: Goldpfunde und sein Pferd"],
            "references": ["731; 24/51"]
          }
        ]
      }
    }
  ],
  "uncertain": false
}
```

**Usage in Nuxt**:
```js
// Lazy load on demand when user selects verb
const verb = await $fetch(`/data/api/verbs/${root}.json`)
```

---

### `data/api/search.json` (Optimized search index, ~500KB)

```json
{
  "turoyo_index": {
    "abəʕ": ["ʔbʕ"],
    "obəʕ": ["ʔbʕ"],
    "ʕbədle": ["ʕbd"],
    "ʕobəd": ["ʕbd"],
    "k-ʕobəd": ["ʕbd"]
  },
  "translation_index": {
    "dienen": ["ʕbd"],
    "wollen": ["ʔbʕ"],
    "haben wollen": ["ʔbʕ"]
  },
  "etymology_index": {
    "Arab.": ["ʕbd", "ʕln", "ʕrf"],
    "MEA": ["ʔbʕ", "ʕbr"]
  }
}
```

**Usage in Nuxt**:
```js
const searchIndex = await $fetch('/data/api/search.json')
// Fast client-side search without loading all verbs
```

---

### `data/api/statistics.json`

```json
{
  "total_verbs": 1240,
  "total_stems": 1752,
  "total_examples": 5483,
  "by_etymology": {
    "Arab.": 484,
    "MEA": 388,
    "Kurd.": 63,
    "Turk.": 20
  },
  "by_binyan": {
    "I": 973,
    "II": 455,
    "III": 299,
    "Detransitive": 459
  },
  "by_letter": {
    "ʔ": 18,
    "ʕ": 156,
    "b": 84
  }
}
```

---

### `data/api/cross-refs.json`

```json
{
  "ʔkl": "ʔxl",
  "ʕwḏ": "ʕwd",
  "mbl": "ybl",
  "rwġ": "rwx"
}
```

---

## Build Process

### `scripts/build-api.js`

```js
#!/usr/bin/env node
import { readdir, readFile, writeFile, mkdir } from 'fs/promises'
import { join } from 'path'

async function buildAPI() {
  console.log('🔨 Building API data from source...')

  // 1. Load all source files
  const sourceDir = 'data/source/verbs'
  const files = await readdir(sourceDir)
  const allVerbs = []

  for (const file of files) {
    const data = JSON.parse(await readFile(join(sourceDir, file), 'utf-8'))
    allVerbs.push(...data.verbs)
  }

  console.log(`📚 Loaded ${allVerbs.length} verbs`)

  // 2. Create individual verb files
  await mkdir('data/api/verbs', { recursive: true })

  for (const verb of allVerbs) {
    const filename = `data/api/verbs/${verb.root}.json`
    await writeFile(filename, JSON.stringify(verb, null, 2))
  }

  console.log(`✅ Created ${allVerbs.length} individual verb files`)

  // 3. Build index
  const index = {
    version: '1.0.0',
    total_verbs: allVerbs.length,
    last_updated: new Date().toISOString(),
    roots: allVerbs.map(v => ({
      root: v.root,
      etymology_source: v.etymology?.source || null,
      binyanim: v.stems.map(s => s.binyan),
      has_detransitive: v.stems.some(s => s.binyan === 'Detransitive'),
      cross_reference: v.cross_reference,
      example_count: v.stems.reduce((sum, s) =>
        sum + Object.values(s.conjugations).flat().length, 0
      ),
      forms: v.stems.flatMap(s => s.forms)
    }))
  }

  await writeFile('data/api/index.json', JSON.stringify(index, null, 2))
  console.log('✅ Created index.json')

  // 4. Build search index
  const searchIndex = {
    turoyo_index: {},
    translation_index: {},
    etymology_index: {}
  }

  for (const verb of allVerbs) {
    // Index forms
    for (const stem of verb.stems) {
      for (const form of stem.forms) {
        if (!searchIndex.turoyo_index[form]) {
          searchIndex.turoyo_index[form] = []
        }
        searchIndex.turoyo_index[form].push(verb.root)
      }

      // Index Turoyo examples
      for (const examples of Object.values(stem.conjugations)) {
        for (const ex of examples) {
          const words = ex.turoyo.split(/\s+/)
          for (const word of words.filter(w => w.length > 2)) {
            if (!searchIndex.turoyo_index[word]) {
              searchIndex.turoyo_index[word] = []
            }
            if (!searchIndex.turoyo_index[word].includes(verb.root)) {
              searchIndex.turoyo_index[word].push(verb.root)
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

  await writeFile('data/api/search.json', JSON.stringify(searchIndex, null, 2))
  console.log('✅ Created search.json')

  // 5. Build statistics
  const stats = {
    total_verbs: allVerbs.length,
    total_stems: allVerbs.reduce((sum, v) => sum + v.stems.length, 0),
    total_examples: allVerbs.reduce((sum, v) =>
      sum + v.stems.reduce((s2, stem) =>
        s2 + Object.values(stem.conjugations).flat().length, 0
      ), 0
    ),
    by_etymology: {},
    by_binyan: {},
    by_letter: {}
  }

  for (const verb of allVerbs) {
    // Etymology stats
    const src = verb.etymology?.source || 'Unknown'
    stats.by_etymology[src] = (stats.by_etymology[src] || 0) + 1

    // Binyan stats
    for (const stem of verb.stems) {
      stats.by_binyan[stem.binyan] = (stats.by_binyan[stem.binyan] || 0) + 1
    }

    // Letter stats
    const letter = verb.root[0]
    stats.by_letter[letter] = (stats.by_letter[letter] || 0) + 1
  }

  await writeFile('data/api/statistics.json', JSON.stringify(stats, null, 2))
  console.log('✅ Created statistics.json')

  // 6. Build cross-references
  const crossRefs = {}
  for (const verb of allVerbs.filter(v => v.cross_reference)) {
    crossRefs[verb.root] = verb.cross_reference
  }

  await writeFile('data/api/cross-refs.json', JSON.stringify(crossRefs, null, 2))
  console.log('✅ Created cross-refs.json')

  console.log('🎉 Build complete!')
}

buildAPI().catch(console.error)
```

---

## GitHub Actions Workflow

### `.github/workflows/build-data.yml`

```yaml
name: Build API Data

on:
  push:
    branches: [main]
    paths:
      - 'data/source/**'
  pull_request:
    paths:
      - 'data/source/**'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Build API data
        run: node scripts/build-api.js

      - name: Validate data
        run: node scripts/validate.js

      - name: Commit built files
        if: github.event_name == 'push'
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/api/
          git diff --quiet && git diff --staged --quiet || \
            git commit -m "chore: rebuild API data [skip ci]"
          git push
```

---

## Nuxt Integration

### `composables/useVerbs.ts`

```ts
export const useVerbs = () => {
  const index = useState<VerbIndex | null>('verbs-index', () => null)
  const searchIndex = useState<SearchIndex | null>('search-index', () => null)

  // Load index once on app init
  const loadIndex = async () => {
    if (!index.value) {
      index.value = await $fetch('/data/api/index.json')
    }
    return index.value
  }

  // Load search index once on first search
  const loadSearchIndex = async () => {
    if (!searchIndex.value) {
      searchIndex.value = await $fetch('/data/api/search.json')
    }
    return searchIndex.value
  }

  // Get single verb (lazy loaded)
  const getVerb = async (root: string) => {
    return await $fetch(`/data/api/verbs/${root}.json`)
  }

  // Search verbs
  const search = async (query: string) => {
    const idx = await loadSearchIndex()
    const roots = new Set<string>()

    // Search in Turoyo index
    for (const [word, verbRoots] of Object.entries(idx.turoyo_index)) {
      if (word.includes(query)) {
        verbRoots.forEach(r => roots.add(r))
      }
    }

    // Search in translation index
    for (const [word, verbRoots] of Object.entries(idx.translation_index)) {
      if (word.toLowerCase().includes(query.toLowerCase())) {
        verbRoots.forEach(r => roots.add(r))
      }
    }

    return Array.from(roots)
  }

  return {
    loadIndex,
    getVerb,
    search
  }
}
```

### Usage in Nuxt pages

```vue
<script setup lang="ts">
const { loadIndex, getVerb, search } = useVerbs()

// Load index on mount
const index = await loadIndex()

// Search
const query = ref('')
const results = ref<string[]>([])

watchDebounced(query, async (q) => {
  if (q.length > 2) {
    results.value = await search(q)
  }
}, { debounce: 300 })

// Get full verb details
const selectedRoot = ref<string | null>(null)
const verb = computed(() =>
  selectedRoot.value ? getVerb(selectedRoot.value) : null
)
</script>
```

---

## PR Workflow for Linguists

### Example: Editing verb ʕbd

1. **Find the file**: `data/source/verbs/ʕ.json`
2. **Edit the verb** (search for `"root": "ʕbd"`)
3. **Commit**: `git commit -m "fix(ʕbd): correct translation"`
4. **Open PR**: Clear diff shows exactly what changed
5. **Auto-build**: GitHub Actions rebuilds `data/api/` on merge
6. **Deploy**: Nuxt app automatically picks up new data

### PR Diff Example

```diff
{
  "root": "ʕbd",
  "stems": [{
    "conjugations": {
      "Infectum": [{
-       "turoyo": "k-ʕobəd l-u=aloho",
+       "turoyo": "k-ʕobəd l-u=alohayḏe",
        "translations": [
-         "er dient Gott"
+         "er dient seinem Gott"
        ]
      }]
    }
  }]
}
```

**Clean, reviewable, conflict-free!**

---

## Benefits Summary

| Aspect | Solution | Benefit |
|--------|----------|---------|
| **PR Reviews** | One file per letter | Clear diffs, easy navigation |
| **Editing** | Plain JSON, organized by letter | Text editor friendly |
| **Performance** | Lazy loading individual verbs | Fast initial load (~100KB) |
| **Search** | Pre-built search index | No need to load all data |
| **Maintenance** | Source → build → deploy | Single source of truth |
| **Caching** | Static JSON files | CDN-friendly, browser cacheable |

---

## File Size Breakdown

```
Source (linguists edit):
  data/source/verbs/*.json      ~3.0MB total (28 files, ~100KB each)

API (Nuxt consumes):
  data/api/index.json           ~100KB  (loads on init)
  data/api/search.json          ~500KB  (loads on first search)
  data/api/verbs/*.json         ~3.0MB total (1,240 files, ~2.5KB each)
  data/api/statistics.json      ~5KB
  data/api/cross-refs.json      ~1KB
```

**Total repo size**: ~6MB (well within GitHub limits)

---

## Next Steps

1. ✅ Run `scripts/build-api.js` to generate API files
2. ✅ Split source data into letter-based files
3. ✅ Set up GitHub Actions
4. ✅ Create Nuxt composables
5. ✅ Deploy and test

Ready to implement?
