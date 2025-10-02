<template>
  <div class="space-y-6 p-6">
    <UCard>
      <template #header>
        <div class="space-y-4">
          <div class="flex flex-col gap-2">
            <h1 class="text-2xl font-semibold tracking-tight">Turoyo Verb Glossary</h1>
            <p class="text-sm text-muted">
              Explore detailed verb entries with stems, examples, translations, and etymology.
            </p>
          </div>

          <div v-if="stats" class="grid gap-4 sm:grid-cols-3">
            <div class="rounded-lg border px-4 py-3">
              <p class="text-xs uppercase text-muted">Verbs</p>
              <p class="text-xl font-semibold">{{ stats.total_verbs }}</p>
            </div>
            <div class="rounded-lg border px-4 py-3">
              <p class="text-xs uppercase text-muted">Stems</p>
              <p class="text-xl font-semibold">{{ stats.total_stems }}</p>
            </div>
            <div class="rounded-lg border px-4 py-3">
              <p class="text-xs uppercase text-muted">Examples</p>
              <p class="text-xl font-semibold">{{ stats.total_examples }}</p>
            </div>
          </div>
        </div>
      </template>

      <div class="space-y-4">
        <UInput
          v-model="q"
          placeholder="Search for roots, forms, translations, or etymology keywords…"
          clearable
          icon="i-heroicons-magnifying-glass"
        />

        <div class="flex flex-wrap items-center gap-3 text-sm text-muted">
          <span>
            Showing {{ displayed.length }} of {{ filtered.length }} matches
          </span>
          <UBadge v-if="q.length" variant="soft">
            Query: {{ q }}
          </UBadge>
        </div>

        <UTable :data="displayed" :columns="columns" :loading="pending">
          <template #root-cell="{ row }">
            <NuxtLink
              :to="`/verbs/${row.original.root}`"
              class="font-semibold text-primary hover:underline"
            >
              {{ row.original.root }}
            </NuxtLink>
          </template>

          <template #etymology_source-cell="{ row }">
            <span class="text-sm">{{ row.original.etymology_source || '—' }}</span>
          </template>

          <template #example_count-cell="{ row }">
            <UBadge color="gray" variant="soft">{{ row.original.example_count }}</UBadge>
          </template>
        </UTable>

        <div
          v-if="q.length >= 2 && filtered.length === 0 && !pending"
          class="rounded-lg border border-dashed px-4 py-6 text-center text-sm text-muted"
        >
          No matches found. Try another keyword or broaden your search.
        </div>
      </div>
    </UCard>

    <UCard>
      <template #header>
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">Browse Filters</h2>
          <div class="text-sm text-muted">Narrow results by letter, etymology, or stem</div>
        </div>
      </template>

      <VerbFilters
        v-model="filters"
        :letters="letterOptions"
        :etymologies="etymologyOptions"
        :stems="stemOptions"
        @reset="resetFilters"
      />
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'
import type { Filters } from '~/types/types/search'

const { loadIndex, loadStatistics, search } = useVerbs()

const pending = ref(false)
const [index, stats] = await Promise.all([loadIndex(), loadStatistics()])

const q = ref('')
const results = ref<string[]>([])
const filters = ref<Filters>({ letter: null, etymology: null, stem: null })

const letterOptions = computed(() => {
  const roots = index?.roots || []
  const letters = Array.from(new Set(roots.map(v => v.root[0]))).sort()
  return letters.map(letter => ({ label: letter, value: letter }))
})

const etymologyOptions = computed(() => {
  if (!stats) return []
  return Object.entries(stats.by_etymology)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([source, count]) => ({
      label: `${source} (${count})`,
      value: source
    }))
})

const stemOptions = computed(() => {
  if (!stats) return []
  return Object.entries(stats.by_stem)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([stem, count]) => ({
      label: `${stem} (${count})`,
      value: stem
    }))
})

function resetFilters() {
  filters.value = { letter: null, etymology: null, stem: null }
}

watch(
  q,
  useDebounceFn(async (value: string) => {
    console.log('[Index] Watch triggered with value:', value)

    if (!value || value.trim().length < 2) {
      console.log('[Index] Query too short, clearing results')
      results.value = []
      pending.value = false
      return
    }

    pending.value = true

    const primary = await search(value, {
      searchTuroyo: true,
      searchTranslations: true,
      searchEtymology: true,
      maxResults: 200
    })

    console.log('[Index] Primary search returned:', primary.length, 'results')

    if (primary.length === 0) {
      console.log('[Index] No primary results, using fallback search')
      const lower = value.toLowerCase()
      const all = index?.roots || []
      const alt = all
        .filter(v => {
          if (v.root.toLowerCase().includes(lower)) return true
          if (v.etymology_source && v.etymology_source.toLowerCase().includes(lower)) return true
          if (v.forms && v.forms.some(f => f.toLowerCase().includes(lower))) return true
          return false
        })
        .map(v => v.root)

      console.log('[Index] Fallback found:', alt.length, 'results')
      results.value = alt.slice(0, 200)
    } else {
      console.log('[Index] Using primary results')
      results.value = primary
    }

    console.log('[Index] Final results.value:', results.value.length, 'results')
    pending.value = false
  }, 250)
)

const filtered = computed(() => {
  const all = index?.roots || []

  if (!q.value || q.value.trim().length < 2) {
    return []
  }

  if (results.value.length === 0) {
    return []
  }

  const matches = new Set(results.value)
  let result = all.filter(v => matches.has(v.root))

  if (filters.value.letter) {
    result = result.filter(v => v.root.startsWith(filters.value.letter as string))
  }

  if (filters.value.etymology) {
    result = result.filter(v => (v.etymology_source || 'Unknown') === filters.value.etymology)
  }

  if (filters.value.stem) {
    result = result.filter(v => v.stems.includes(filters.value.stem as string))
  }

  console.log('[Index] Filtered result count:', result.length)
  return result
})

const displayed = computed(() => {
  const result = filtered.value.slice(0, 200)
  console.log('[Index] Displayed count:', result.length)
  if (result.length > 0) {
    console.log('[Index] First displayed item:', result[0])
  }
  return result
})

const columns = [
  {
    accessorKey: 'root',
    header: 'Root'
  },
  {
    accessorKey: 'etymology_source',
    header: 'Etymology'
  },
  {
    accessorKey: 'example_count',
    header: 'Examples'
  }
]
</script>

