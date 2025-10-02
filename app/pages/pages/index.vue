<template>
  <div class="space-y-8">
    <UCard>
      <template #header>
        <div class="flex flex-col gap-1">
          <h1 class="text-2xl font-semibold">Turoyo Verb Glossary</h1>
          <p class="text-sm text-muted">
            {{ stats?.total_verbs }} verbs · {{ stats?.total_stems }} stems · {{ stats?.total_examples }} examples
          </p>
        </div>
      </template>

      <div class="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <div class="space-y-4">
          <UInput
            v-model="searchState.query"
            placeholder="Search Turoyo, translations, etymology, references..."
            icon="i-heroicons-magnifying-glass"
            clearable
            @clear="resetSearch"
          />

          <div class="flex flex-wrap gap-3 items-center">
            <UToggle v-model="searchState.fullText" label="Full-text in examples" />
            <UToggle v-model="searchState.includeTranslations" label="Match translations" />
            <UToggle v-model="searchState.includeEtymology" label="Match etymology" />
          </div>

          <div class="grid gap-3 md:grid-cols-3">
            <USelect
              v-model="filters.letter"
              :options="letters"
              placeholder="All letters"
              option-attribute="label"
            />
            <USelect
              v-model="filters.etymology"
              :options="etymologySources"
              placeholder="All etymologies"
              option-attribute="label"
            />
            <USelect
              v-model="filters.binyan"
              :options="binyanim"
              placeholder="All binyanim"
              option-attribute="label"
            />
          </div>
        </div>

        <div class="space-y-4">
          <div class="grid gap-3">
            <UStat title="Search results" :value="filteredVerbs.length" icon="i-heroicons-magnifying-glass-circle" />
            <UStat
              title="Currently loaded"
              :description="selectedRoots.length ? `${selectedRoots.length} selected` : 'Filter to narrow results'"
              :value="displayedVerbs.length"
              icon="i-heroicons-list-bullet"
            />
          </div>

          <UButton
            color="primary"
            variant="soft"
            icon="i-heroicons-chart-bar"
            to="/statistics"
          >
            View analytics
          </UButton>
        </div>
      </div>
    </UCard>

    <div class="grid gap-6 lg:grid-cols-[2fr,1fr]">
      <UCard class="lg:col-span-2">
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold">Verb Results</h2>
            <UButton
              v-if="filtersActive"
              color="gray"
              variant="ghost"
              size="xs"
              icon="i-heroicons-arrow-path"
              @click="resetFilters"
            >
              Reset filters
            </UButton>
          </div>
        </template>

        <div class="overflow-x-auto">
          <UTable :rows="displayedVerbs" :columns="columns" />
        </div>
      </UCard>

      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold">Insights</h2>
            <UBadge color="primary" variant="soft">Preview</UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <UAlert
            v-if="selectedRoots.length"
            title="Selected verbs"
            color="primary"
            :description="selectedRoots.join(', ')"
            icon="i-heroicons-arrow-right-circle"
          />

          <div v-for="insight in insights" :key="insight.title" class="border rounded-lg px-4 py-3 space-y-1">
            <div class="flex items-center gap-2">
              <UIcon :name="insight.icon" class="h-5 w-5" />
              <p class="font-medium">{{ insight.title }}</p>
            </div>
            <p class="text-sm text-muted">
              {{ insight.description }}
            </p>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import type { VerbIndexEntry } from '~/composables/useVerbs'

const { loadIndex, loadStatistics, search } = useVerbs()

const [index, stats] = await Promise.all([loadIndex(), loadStatistics()])

const searchState = reactive({
  query: '',
  fullText: true,
  includeTranslations: true,
  includeEtymology: true
})

const filters = reactive({
  letter: null as string | null,
  etymology: null as string | null,
  binyan: null as string | null
})

const searchResults = useState<string[]>('search-results', () => [])

watch(
  () => ({ ...searchState }),
  useDebounceFn(async current => {
    const { query } = current

    if (!query || query.trim().length < 2) {
      searchResults.value = []
      return
    }

    const results = await search(query, {
      searchTuroyo: searchState.fullText,
      searchTranslations: searchState.includeTranslations,
      searchEtymology: searchState.includeEtymology,
      maxResults: 200
    })

    searchResults.value = results
  }, 250),
  { deep: true }
)

const filteredVerbs = computed(() => {
  const all = index?.roots || []
  const roots = searchResults.value.length ? new Set(searchResults.value) : null

  const base = roots ? all.filter(v => roots.has(v.root)) : all

  return base.filter(verb => {
    if (filters.letter && !verb.root.startsWith(filters.letter)) return false
    if (filters.etymology && verb.etymology_source !== filters.etymology) return false
    if (filters.binyan && !verb.binyanim.includes(filters.binyan)) return false
    return true
  })
})

const displayedVerbs = computed(() => filteredVerbs.value.slice(0, 200))
const selectedRoots = computed(() => searchResults.value.slice(0, 10))

const columns = [
  {
    key: 'root',
    label: 'Root',
    sortable: true,
    render: (row: VerbIndexEntry) => h(
      NuxtLink,
      { to: `/verbs/${row.root}`, class: 'font-semibold text-primary' },
      { default: () => row.root }
    )
  },
  {
    key: 'forms',
    label: 'Forms',
    render: (row: VerbIndexEntry) => row.forms.slice(0, 4).join(', ')
  },
  {
    key: 'etymology_source',
    label: 'Etymology',
    sortable: true,
    render: (row: VerbIndexEntry) => row.etymology_source || '—'
  },
  {
    key: 'binyanim',
    label: 'Binyanim',
    render: (row: VerbIndexEntry) => row.binyanim.join(', ')
  },
  {
    key: 'example_count',
    label: 'Examples',
    sortable: true
  }
]

const letters = computed(() => [
  { label: 'All letters', value: null },
  ...Object.entries(stats?.by_letter || {})
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([letter, count]) => ({ label: `${letter} (${count})`, value: letter }))
])

const etymologySources = computed(() => [
  { label: 'All etymologies', value: null },
  ...Object.entries(stats?.by_etymology || {})
    .sort((a, b) => b[1] - a[1])
    .map(([source, count]) => ({ label: `${source} (${count})`, value: source }))
])

const binyanim = computed(() => [
  { label: 'All binyanim', value: null },
  ...Object.entries(stats?.by_binyan || {})
    .sort((a, b) => b[1] - a[1])
    .map(([binyan, count]) => ({ label: `${binyan} (${count})`, value: binyan }))
])

const filtersActive = computed(() => Boolean(filters.letter || filters.etymology || filters.binyan))

const insights = computed(() => {
  const topEtymology = Object.entries(stats?.by_etymology || {}).sort((a, b) => b[1] - a[1])[0]
  const topBinyan = Object.entries(stats?.by_binyan || {}).sort((a, b) => b[1] - a[1])[0]

  return [
    {
      title: 'Dominant etymology source',
      description: topEtymology ? `${topEtymology[0]} (${topEtymology[1]} verbs)` : 'No data',
      icon: 'i-heroicons-language'
    },
    {
      title: 'Most common binyan',
      description: topBinyan ? `${topBinyan[0]} (${topBinyan[1]} stems)` : 'No data',
      icon: 'i-heroicons-sparkles'
    },
    {
      title: 'Current search scope',
      description: filtersActive.value
        ? `Filtered to ${filteredVerbs.value.length} entries`
        : 'Full dataset visible',
      icon: 'i-heroicons-funnel'
    }
  ]
})

function resetFilters() {
  filters.letter = null
  filters.etymology = null
  filters.binyan = null
}

function resetSearch() {
  searchState.query = ''
}
</script>
