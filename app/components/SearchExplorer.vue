<template>
    <div class="search">
        <form class="search-form" role="search" @submit.prevent="run">
            <label :for="inputId" class="sr-only">Search roots, forms, meanings, examples and texts</label>
            <input
                :id="inputId"
                v-model="query"
                type="search"
                placeholder="Search roots, forms, meanings, examples and texts, e.g. sym or wollen"
                autocomplete="off"
            />
            <label class="regex small"><input v-model="regex" type="checkbox"/> Regular expression</label>
            <span class="small muted">Vowel and stress marks are optional.</span>
        </form>
        <p v-if="pending" role="status" class="small">
            Searching…
        </p>
        <p v-else-if="error" class="error" role="alert">
            {{ error }}
        </p>
        <template v-else-if="response">
            <p class="small muted" aria-live="polite">
                {{ response.total.toLocaleString("en") }} matches.
            </p>
            <section v-for="group in groups" :key="group.type" class="result-group">
                <h2>
                    {{ group.label }}
                    <span class="small muted">{{ groupCount(group) }}</span>
                </h2>
                <NuxtLink
                    v-for="result in group.results"
                    :key="result.id"
                    :to="result.to"
                    class="result"
                >
                    <span class="result-title serif" v-text="result.title"></span>
                    <MatchSnippet class="result-snippet" :text="result.snippet" :ranges="result.ranges"/>
                </NuxtLink>
            </section>
            <p v-if="!response.total" class="empty">
                No matches. Try a shorter word or a different spelling.
            </p>
        </template>
    </div>
</template>

<script setup lang="ts">
import { watchDebounced } from '@vueuse/core'
import type { ISearchResult } from '#shared/types/ISearchResult'

const query = defineModel<string>({ default: '' })
const inputId = useId()
const regex = ref(false)
const pending = ref(false)
const error = ref('')
const response = ref<{
    results: ISearchResult[]
    counts: Record<string, number>
    total: number
} | null>(null)
let requestId = 0
async function run() {
    const current = ++requestId
    if (!query.value.trim()) {
        response.value = null
        pending.value = false
        return
    }
    pending.value = true
    error.value = ''
    try {
        const data = await $fetch('/api/glossary/search', {
            query: {
                q: query.value,
                regex: regex.value,
            },
        })
        if (current === requestId) response.value = data
    }
    catch (cause) {
        if (current === requestId)
            error.value = (cause as { data?: { message?: string } }).data?.message
                || 'Search could not be completed. Please try again.'
    }
    finally {
        if (current === requestId) pending.value = false
    }
}
watchDebounced([query, regex], run, { debounce: 300 })
onMounted(() => {
    if (query.value) run()
})
const labels = {
    root: 'Roots',
    form: 'Turoyo forms',
    gloss: 'Meanings',
    example: 'Glossary examples',
    text: 'From the texts',
}
function groupCount(group: { count: number
    results: ISearchResult[] }) {
    return group.count > group.results.length ? `${group.count}, first ${group.results.length} shown` : `${group.count}`
}
const groups = computed(() =>
    Object.entries(labels)
        .map(([type, label]) => ({
            type,
            label,
            count: response.value?.counts[type] || 0,
            results: response.value?.results.filter(result => result.type === type) || [],
        }))
        .filter(group => group.results.length)
)
</script>

<style scoped>
.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem 1rem;
}
.search-form input[type="search"] {
  flex: 1 1 24rem;
  max-width: 44rem;
}
.regex {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}
.search > p {
  margin-top: 0.5rem;
}
.result-group {
  margin-top: 1rem;
}
.result-group h2 {
  padding-bottom: 0.2rem;
  border-bottom: 2px solid var(--ink);
  font-size: 1rem;
}
.result {
  display: grid;
  grid-template-columns: 16rem minmax(0, 1fr);
  gap: 0 1rem;
  padding: 0.2rem 0;
  border-bottom: 1px solid var(--rule);
  color: var(--ink);
  font-size: 0.9375rem;
  text-decoration: none;
}
.result:hover {
  background: var(--bg-soft);
}
.result-title {
  color: var(--accent);
  font-size: 1rem;
}
.result:hover .result-title {
  text-decoration: underline;
}
@media (max-width: 760px) {
  .result {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
