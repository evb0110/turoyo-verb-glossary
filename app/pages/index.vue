<template>
  <div class="p-6">
    <UCard>
      <template #header>
        <h1 class="text-xl font-semibold">Turoyo Verb Glossary</h1>
      </template>

      <p v-if="!index">Loading…</p>
      <div v-else class="space-y-4">
        <p class="text-sm text-muted">
          {{ stats?.total_verbs }} verbs · {{ stats?.total_stems }} stems · {{ stats?.total_examples }} examples
        </p>

        <UInput v-model="q" placeholder="Search…" clearable />

        <UTable :data="displayed" :columns="columns">
          <template #root-cell="{ row }">
            <NuxtLink
              :to="`/verbs/${row.original.root}`"
              class="font-semibold text-primary hover:underline"
            >
              {{ row.original.root }}
            </NuxtLink>
          </template>
        </UTable>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const { loadIndex, loadStatistics, search } = useVerbs()

const [index, stats] = await Promise.all([loadIndex(), loadStatistics()])

const q = ref('')
const results = ref<string[]>([])

watch(
  q,
  useDebounceFn(async (value: string) => {
    console.log('[Index] Watch triggered with value:', value)

    if (!value || value.trim().length < 2) {
      console.log('[Index] Query too short, clearing results')
      results.value = []
      return
    }

    const primary = await search(value, {
      searchTuroyo: true,
      searchTranslations: true,
      searchEtymology: true,
      maxResults: 200
    })

    console.log('[Index] Primary search returned:', primary.length, 'results')

    // Fallback: if no matches in prebuilt indices, do a lightweight scan over the index
    if (primary.length === 0) {
      console.log('[Index] No primary results, using fallback search')
      const q = value.toLowerCase()
      const all = index?.roots || []
      const alt = all.filter(v => {
        if (v.root.toLowerCase().includes(q)) return true
        if (v.etymology_source && v.etymology_source.toLowerCase().includes(q)) return true
        if (v.forms && v.forms.some(f => f.toLowerCase().includes(q))) return true
        return false
      }).map(v => v.root)
      console.log('[Index] Fallback found:', alt.length, 'results')
      results.value = alt.slice(0, 200)
    } else {
      console.log('[Index] Using primary results')
      results.value = primary
    }

    console.log('[Index] Final results.value:', results.value.length, 'results')
  }, 250)
)

const filtered = computed(() => {
  const all = index?.roots || []

  // If no search query, return empty array (don't show all verbs)
  if (!q.value || q.value.trim().length < 2) {
    return []
  }

  // If no results from search, return empty array
  if (results.value.length === 0) {
    return []
  }

  const set = new Set(results.value)
  console.log('[Index] Filtered computing:', {
    all_count: all.length,
    results_count: results.value.length,
    set_size: set.size
  })

  const result = all.filter(v => set.has(v.root))
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

