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

        <UTable :rows="displayed" :columns="columns" />
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
    if (!value || value.trim().length < 2) {
      results.value = []
      return
    }
    const primary = await search(value, {
      searchTuroyo: true,
      searchTranslations: true,
      searchEtymology: true,
      maxResults: 200
    })

    // Fallback: if no matches in prebuilt indices, do a lightweight scan over the index
    if (primary.length === 0) {
      const q = value.toLowerCase()
      const all = index?.roots || []
      const alt = all.filter(v => {
        if (v.root.toLowerCase().includes(q)) return true
        if (v.etymology_source && v.etymology_source.toLowerCase().includes(q)) return true
        if (v.forms && v.forms.some(f => f.toLowerCase().includes(q))) return true
        return false
      }).map(v => v.root)
      results.value = alt.slice(0, 200)
    } else {
      results.value = primary
    }
  }, 250)
)

const filtered = computed(() => {
  const all = index?.roots || []
  const set = results.value.length ? new Set(results.value) : null
  return (set ? all.filter(v => set.has(v.root)) : all)
})

const displayed = computed(() => filtered.value.slice(0, 200))

const columns = [
  {
    id: 'root',
    accessorKey: 'root',
    header: 'Root',
    cell: (ctx: any) => {
      const root = ctx.row?.original?.root as string
      return h(
        NuxtLink,
        { to: `/verbs/${root}`, class: 'font-semibold text-primary' },
        { default: () => root }
      )
    }
  },
  { id: 'etymology_source', accessorKey: 'etymology_source', header: 'Etymology' },
  { id: 'example_count', accessorKey: 'example_count', header: 'Examples' }
]
</script>

