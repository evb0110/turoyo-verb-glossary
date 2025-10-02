# Turoyo Verb Glossary - Quick Start

## 🚀 Quick Start Guide

### 1. Build API Data

```bash
npm run build
```

This generates all API files from source data:
- ✅ 1,240 individual verb files
- ✅ index.json (359KB)
- ✅ search.json (2.2MB)
- ✅ statistics.json
- ✅ cross-refs.json

### 2. Validate Data

```bash
npm run validate
```

### 3. Use in Nuxt

#### Example 1: Browse All Verbs

```vue
<script setup lang="ts">
const { loadIndex } = useVerbs()
const index = await loadIndex()
</script>

<template>
  <div>
    <h1>{{ index.total_verbs }} Turoyo Verbs</h1>
    <ul>
      <li v-for="verb in index.roots" :key="verb.root">
        <NuxtLink :to="`/verbs/${verb.root}`">
          {{ verb.root }}
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>
```

#### Example 2: Search Verbs

```vue
<script setup lang="ts">
const { search } = useVerbs()
const query = ref('')
const results = ref([])

watchDebounced(query, async (q) => {
  if (q.length > 2) {
    results.value = await search(q)
  }
}, { debounce: 300 })
</script>

<template>
  <input v-model="query" placeholder="Search..." />
  <p>Found {{ results.length }} verbs</p>
</template>
```

#### Example 3: Display Verb Details

```vue
<script setup lang="ts">
const route = useRoute()
const { getVerb } = useVerbs()

const verb = await getVerb(route.params.root)
</script>

<template>
  <div>
    <h1>{{ verb.root }}</h1>
    <p>{{ verb.etymology?.meaning }}</p>

    <div v-for="stem in verb.stems" :key="stem.binyan">
      <h2>Binyan {{ stem.binyan }}</h2>
      <p>Forms: {{ stem.forms.join(', ') }}</p>
    </div>
  </div>
</template>
```

## 📁 Project Structure

```
turoyo-verb-glossary/
├── .github/workflows/
│   └── build-data.yml          # Auto-build on push
├── composables/
│   └── useVerbs.ts             # Nuxt composable
├── pages/
│   ├── index.vue               # Browse/search page
│   └── verbs/[root].vue        # Verb detail page
├── scripts/
│   ├── build-api.js            # Build script
│   └── validate.js             # Validation script
├── data/
│   ├── source/verbs/           # Source data (edit here)
│   └── api/                    # Generated API files
│       ├── index.json
│       ├── search.json
│       ├── statistics.json
│       ├── cross-refs.json
│       └── verbs/              # 1,240 individual files
├── package.json
├── README_NUXT.md              # Full documentation
└── INTEGRATION_SUMMARY.md      # Implementation details
```

## 🔧 API Methods

### Data Loading
```typescript
const { loadIndex, loadSearchIndex, loadStatistics, loadCrossReferences } = useVerbs()

await loadIndex()              // Load once on app init
await loadSearchIndex()        // Load on first search
await loadStatistics()         // Load stats
await loadCrossReferences()    // Load cross-refs
```

### Verb Access
```typescript
const { getVerb, getVerbWithCrossRef } = useVerbs()

const verb = await getVerb('ʔbʕ')
const verb2 = await getVerbWithCrossRef('ʔkl')  // Follows cross-refs
```

### Search & Filter
```typescript
const { search, getVerbsByEtymology, getVerbsByBinyan, getVerbsByLetter } = useVerbs()

const results = await search('dienen')
const arabicVerbs = await getVerbsByEtymology('Arab.')
const binyan1 = await getVerbsByBinyan('I')
const alephVerbs = await getVerbsByLetter('ʔ')
```

## 📊 Statistics

- **1,240 verbs** across 29 letters
- **2,211 stems** (I, II, III, Detransitive)
- **5,483 examples** with translations
- **15 cross-references**

### Etymology Distribution
- MEA: 403 verbs
- Arab.: 492 verbs
- Kurd.: 66 verbs
- Turk.: 20 verbs
- Others: ~259 verbs

## 🔄 GitHub Actions

Automatically rebuilds API data when source files change:

1. Edit `data/source/verbs/*.json`
2. Push to `main` branch
3. GitHub Actions runs build and validate
4. Built files auto-committed to `data/api/`

## 📝 NPM Scripts

```bash
npm run build        # Build API files
npm run validate     # Validate data integrity
npm run build:all    # Build + validate
```

## 🎨 Example Pages

### Homepage (`/`)
- Search all verbs
- Filter by letter, etymology, binyan
- Browse complete verb list
- Responsive table view

### Verb Details (`/verbs/[root]`)
- Full verb information
- Etymology details
- All stems and conjugations
- Examples with translations
- Cross-reference handling

## 📚 Documentation

- **README_NUXT.md** - Complete integration guide
- **INTEGRATION_SUMMARY.md** - Implementation summary
- **DATA_ARCHITECTURE.md** - System architecture

## 🚨 Common Tasks

### Rebuild API Data
```bash
npm run build
```

### Check Data Integrity
```bash
npm run validate
```

### Add New Verb
1. Edit appropriate file in `data/source/verbs/`
2. Run `npm run build`
3. Run `npm run validate`
4. Commit both source and API files

### Search Examples
```typescript
// Search Turoyo text
await search('abəʕ')

// Search German translation
await search('dienen')

// Search etymology
await search('Arab.')

// Custom search options
await search('wollen', {
  searchTuroyo: true,
  searchTranslations: true,
  searchEtymology: false,
  maxResults: 50
})
```

## 🔗 Links

- GitHub Actions: `.github/workflows/build-data.yml`
- Composable: `composables/useVerbs.ts`
- Example Pages: `pages/index.vue`, `pages/verbs/[root].vue`
- Build Script: `scripts/build-api.js`
- Validate Script: `scripts/validate.js`

---

**Ready to use!** Start with `npm run build` then explore the example pages.
