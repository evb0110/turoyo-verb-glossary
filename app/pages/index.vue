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

        <div v-if="displayed.length === 0" class="text-center py-8 text-gray-500">
          No data
        </div>

        <div v-else class="border rounded">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Root</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Etymology</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Examples</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="row in displayed" :key="row.root">
                <td class="px-6 py-4 whitespace-nowrap">
                  <NuxtLink :to="`/verbs/${row.root}`" class="font-semibold text-primary hover:underline">
                    {{ row.root }}
                  </NuxtLink>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ row.etymology_source || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ row.example_count }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import type { VerbIndexEntry } from '~/composables/useVerbs'

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
  const set = results.value.length ? new Set(results.value) : null
  console.log('[Index] Filtered computing:', {
    all_count: all.length,
    results_count: results.value.length,
    set_size: set?.size,
    has_set: !!set
  })

  if (set && all.length > 0 && results.value.length > 0) {
    console.log('[Index] Sample results:', results.value.slice(0, 5))
    console.log('[Index] Sample index roots:', all.slice(0, 5).map(v => v.root))
  }

  const result = (set ? all.filter(v => set.has(v.root)) : all)
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
    id: 'root',
    key: 'root',
    label: 'Root'
  },
  {
    id: 'etymology_source',
    key: 'etymology_source',
    label: 'Etymology'
  },
  {
    id: 'example_count',
    key: 'example_count',
    label: 'Examples'
  }
]
</script>

