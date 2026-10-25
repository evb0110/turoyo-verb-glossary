<template>
    <div class="search-explorer">
        <form class="search-form" @submit.prevent="run">
            <label :for="inputId">Find a verb: root, form or meaning</label>
            <input
                :id="inputId"
                v-model="query"
                type="search"
                placeholder="e.g. sym or put"
                autocomplete="off"
            />
            <button class="primary" type="submit">
                Search
            </button>
        </form>
        <details class="search-options">
            <summary>More options</summary>
            <label class="row"><input v-model="regex" type="checkbox"/> Use a regular
                expression</label>
            <p class="caption">
                Special transcription marks are optional in ordinary searches.
            </p>
        </details>
        <p v-if="pending" role="status">
            Searching…
        </p>
        <p v-else-if="error" class="error" role="alert">
            {{ error }}
        </p>
        <template v-else-if="response">
            <p class="muted" aria-live="polite">
                {{ response.total }} matches. Up to 30 shown in each group.
            </p>
            <section v-for="group in groups" :key="group.type" class="result-group">
                <h2>{{ group.label }}</h2>
                <NuxtLink
                    v-for="result in group.results"
                    :key="result.id"
                    :to="result.to"
                    class="search-result"
                >
                    <span class="result-title">{{ result.title }}</span>
                    <MatchSnippet :text="result.snippet" :ranges="result.ranges"/>
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
            error.value
                = (cause as { data?: { message?: string } }).data?.message
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
const groups = computed(() =>
    Object.entries(labels)
        .map(([type, label]) => ({
            type,
            label,
            results:
        response.value?.results.filter(result => result.type === type) || [],
        }))
        .filter(group => group.results.length)
)
</script>

<style scoped>
.search-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.7rem;
}
.search-form label {
  grid-column: 1 / -1;
}
.search-options {
  margin: 0.7rem 0 1.4rem;
}
.search-options .caption {
  margin-top: 0.7rem;
}
.result-group {
  margin-top: 1.8rem;
}
.search-result {
  display: grid;
  gap: 0.4rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--rule);
  color: var(--ink);
  text-decoration: none;
}
.result-title {
  color: var(--accent);
  font-family: var(--font-serif);
  font-size: 1.4rem;
}
</style>
