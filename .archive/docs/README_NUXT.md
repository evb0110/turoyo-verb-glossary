# Turoyo Verb Glossary - Nuxt Integration Guide

This guide explains how to integrate the Turoyo Verb Glossary data into your Nuxt application.

## Overview

The verb glossary uses a two-tier data architecture:

1. **Source data** (`data/source/verbs/`) - Organized by letter, edited by linguists
2. **API data** (`data/api/`) - Optimized for web consumption, auto-generated from source

## Quick Start

### 1. Build API Data

First, generate the API files from your source data:

```bash
# Build all API files
node scripts/build-api.js

# Validate the generated data
node scripts/validate.js
```

This creates:
- `data/api/index.json` - Lightweight index (~100KB)
- `data/api/search.json` - Search index (~500KB)
- `data/api/statistics.json` - Pre-computed statistics
- `data/api/cross-refs.json` - Cross-reference mappings
- `data/api/verbs/*.json` - Individual verb files (~1,240 files)

### 2. Use the Composable

The `useVerbs()` composable provides all functionality you need:

```typescript
// In your Nuxt component
const { loadIndex, getVerb, search } = useVerbs()

// Load index on app init
const index = await loadIndex()

// Get a specific verb
const verb = await getVerb('ʔbʕ')

// Search for verbs
const results = await search('dienen')
```

### 3. Example Pages

#### Browse All Verbs

```vue
<script setup lang="ts">
const { loadIndex } = useVerbs()
const index = await loadIndex()

const selectedLetter = ref('')
const filteredVerbs = computed(() => {
  if (!selectedLetter.value) return index.roots
  return index.roots.filter(v => v.root.startsWith(selectedLetter.value))
})
</script>

<template>
  <div>
    <h1>Turoyo Verbs ({{ index.total_verbs }})</h1>

    <!-- Letter filter -->
    <div class="letter-filter">
      <button @click="selectedLetter = ''">All</button>
      <button
        v-for="letter in Object.keys(statistics?.by_letter || {})"
        :key="letter"
        @click="selectedLetter = letter"
      >
        {{ letter }}
      </button>
    </div>

    <!-- Verb list -->
    <ul>
      <li v-for="verb in filteredVerbs" :key="verb.root">
        <NuxtLink :to="`/verbs/${verb.root}`">
          {{ verb.root }}
        </NuxtLink>
        <span class="forms">{{ verb.forms.join(', ') }}</span>
        <span class="etymology">{{ verb.etymology_source }}</span>
      </li>
    </ul>
  </div>
</template>
```

#### Search Verbs

```vue
<script setup lang="ts">
const { search, loadIndex } = useVerbs()

const query = ref('')
const results = ref<string[]>([])
const index = await loadIndex()

// Debounced search
watchDebounced(query, async (q) => {
  if (q.length > 2) {
    results.value = await search(q)
  } else {
    results.value = []
  }
}, { debounce: 300 })

// Get verb details for results
const verbDetails = computed(() => {
  return results.value.map(root =>
    index.roots.find(v => v.root === root)
  ).filter(Boolean)
})
</script>

<template>
  <div>
    <h1>Search Verbs</h1>

    <input
      v-model="query"
      type="search"
      placeholder="Search Turoyo, German, or etymology..."
    />

    <div v-if="results.length > 0">
      <p>Found {{ results.length }} verbs</p>
      <ul>
        <li v-for="verb in verbDetails" :key="verb.root">
          <NuxtLink :to="`/verbs/${verb.root}`">
            {{ verb.root }}
          </NuxtLink>
          <span>{{ verb.forms.join(', ') }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>
```

#### Statistics Dashboard

```vue
<script setup lang="ts">
const { loadStatistics } = useVerbs()
const stats = await loadStatistics()
</script>

<template>
  <div>
    <h1>Statistics</h1>

    <div class="stat-grid">
      <div class="stat-card">
        <h3>Total Verbs</h3>
        <p class="number">{{ stats.total_verbs }}</p>
      </div>

      <div class="stat-card">
        <h3>Total Stems</h3>
        <p class="number">{{ stats.total_stems }}</p>
      </div>

      <div class="stat-card">
        <h3>Total Examples</h3>
        <p class="number">{{ stats.total_examples }}</p>
      </div>
    </div>

    <div class="chart">
      <h2>By Etymology</h2>
      <div v-for="(count, source) in stats.by_etymology" :key="source">
        <span>{{ source }}</span>: {{ count }}
      </div>
    </div>

    <div class="chart">
      <h2>By Binyan</h2>
      <div v-for="(count, binyan) in stats.by_binyan" :key="binyan">
        <span>{{ binyan }}</span>: {{ count }}
      </div>
    </div>
  </div>
</template>
```

## API Reference

### `useVerbs()` Composable

#### Data Loading Methods

```typescript
// Load index (call once on app init)
const index: VerbIndex = await loadIndex()

// Load search index (call on first search)
const searchIndex: SearchIndex = await loadSearchIndex()

// Load statistics
const stats: Statistics = await loadStatistics()

// Load cross-references
const crossRefs: CrossReferences = await loadCrossReferences()
```

#### Single Verb Access

```typescript
// Get a verb by root
const verb: Verb = await getVerb('ʔbʕ')

// Get a verb, following cross-references
const verb: Verb = await getVerbWithCrossRef('ʔkl') // redirects to 'ʔxl'
```

#### Search and Filtering

```typescript
// Search across all fields
const roots: string[] = await search('dienen')

// Search with options
const roots: string[] = await search('dienen', {
  searchTuroyo: true,        // default: true
  searchTranslations: true,  // default: true
  searchEtymology: false,    // default: true
  maxResults: 50            // default: 100
})

// Get verbs by etymology source
const arabicVerbs: string[] = await getVerbsByEtymology('Arab.')

// Get verbs by binyan
const binyan1: VerbIndexEntry[] = await getVerbsByBinyan('I')

// Get verbs by letter
const alephVerbs: VerbIndexEntry[] = await getVerbsByLetter('ʔ')
```

### Type Definitions

```typescript
interface Verb {
  root: string
  etymology: Etymology | null
  cross_reference: string | null
  stems: Stem[]
  uncertain: boolean
}

interface Stem {
  binyan: string
  forms: string[]
  conjugations: {
    [key: string]: Example[]
  }
}

interface Example {
  turoyo: string
  translations: string[]
  references: string[]
}

interface VerbIndexEntry {
  root: string
  etymology_source: string | null
  binyanim: string[]
  has_detransitive: boolean
  cross_reference: string | null
  example_count: number
  forms: string[]
}
```

## Performance Tips

### 1. Load Data Progressively

```typescript
// App initialization - load only index (~100KB)
const index = await loadIndex()

// On first search - load search index (~500KB)
const searchIndex = await loadSearchIndex()

// Individual verbs - load on demand (~2-5KB each)
const verb = await getVerb(selectedRoot)
```

### 2. Use Caching

The composable automatically caches loaded data using Nuxt's `useState`:

```typescript
// First call loads from server
await loadIndex()

// Subsequent calls use cached data
await loadIndex() // instant
```

### 3. Prefetch Common Verbs

```vue
<script setup lang="ts">
// Prefetch popular verbs
const popularRoots = ['ʕbd', 'ʕrf', 'ʕmr']
onMounted(() => {
  popularRoots.forEach(root => {
    // Prefetch in background
    getVerb(root)
  })
})
</script>
```

## GitHub Actions Workflow

The repository includes a GitHub Actions workflow that automatically rebuilds API data when source files change.

### Workflow: `.github/workflows/build-data.yml`

**Triggers:**
- Push to `main` branch when `data/source/**` changes
- Pull requests modifying `data/source/**`

**Steps:**
1. Checkout code
2. Setup Node.js 20
3. Run `node scripts/build-api.js`
4. Run `node scripts/validate.js`
5. Commit and push built files (only on push to main)

### Manual Build

You can also manually rebuild the data:

```bash
# Build
node scripts/build-api.js

# Validate
node scripts/validate.js
```

## Project Structure

```
turoyo-verb-glossary/
├── data/
│   ├── source/              # Source data (edit these)
│   │   ├── verbs/
│   │   │   ├── ʔ.json
│   │   │   ├── ʕ.json
│   │   │   └── ...
│   │   └── metadata.json
│   │
│   └── api/                 # Built artifacts (generated)
│       ├── verbs/
│       │   ├── ʔbʕ.json
│       │   └── ...
│       ├── index.json
│       ├── search.json
│       ├── statistics.json
│       └── cross-refs.json
│
├── scripts/
│   ├── build-api.js         # Build script
│   └── validate.js          # Validation script
│
├── composables/
│   └── useVerbs.ts          # Nuxt composable
│
├── pages/
│   └── verbs/
│       └── [root].vue       # Example verb detail page
│
└── .github/
    └── workflows/
        └── build-data.yml   # GitHub Actions
```

## Development Workflow

### For Linguists (Editing Data)

1. Edit source files in `data/source/verbs/{letter}.json`
2. Run `node scripts/build-api.js` to rebuild
3. Run `node scripts/validate.js` to check integrity
4. Commit both source and API files
5. GitHub Actions will auto-rebuild on push

### For Developers (Using Data)

1. Import the composable: `const { loadIndex, getVerb } = useVerbs()`
2. Load index on app init
3. Use search/filtering methods as needed
4. Lazy load individual verbs when needed

## Advanced Usage

### Custom Search Logic

```typescript
const { loadSearchIndex, loadIndex } = useVerbs()

async function customSearch(query: string) {
  const searchIdx = await loadSearchIndex()
  const index = await loadIndex()

  const roots = new Set<string>()

  // Custom logic: only search in forms
  for (const [form, verbRoots] of Object.entries(searchIdx.turoyo_index)) {
    if (form.startsWith(query)) {
      verbRoots.forEach(r => roots.add(r))
    }
  }

  // Return full details
  return Array.from(roots).map(root =>
    index.roots.find(v => v.root === root)
  )
}
```

### Batch Loading

```typescript
async function loadMultipleVerbs(roots: string[]) {
  return await Promise.all(
    roots.map(root => getVerb(root))
  )
}
```

### Analytics

```typescript
const { loadStatistics } = useVerbs()

async function analyzeEtymology() {
  const stats = await loadStatistics()

  const entries = Object.entries(stats.by_etymology)
  const total = stats.total_verbs

  return entries.map(([source, count]) => ({
    source,
    count,
    percentage: (count / total * 100).toFixed(2)
  }))
}
```

## Troubleshooting

### Build Fails

```bash
# Check Node version (requires 20+)
node --version

# Install dependencies if needed
npm install

# Check source data integrity
node scripts/validate.js
```

### Missing Data Files

```bash
# Rebuild all API files
node scripts/build-api.js
```

### GitHub Actions Not Running

Check:
- Workflow file is in `.github/workflows/`
- Push includes changes to `data/source/**`
- GitHub Actions is enabled in repository settings

## License

See main README.md for license information.

## Support

For questions or issues, please open an issue on GitHub.
