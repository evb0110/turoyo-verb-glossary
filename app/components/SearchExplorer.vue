<template>
    <div class="search-explorer">
        <form class="search-form" @submit.prevent="run">
            <label class="sr-only" :for="inputId">
                Search roots, forms, glosses and texts
            </label>
            <input
                :id="inputId"
                ref="input"
                v-model="query"
                :autofocus="autofocus"
                placeholder="A root, a word, a meaning…"
                autocomplete="off"
            />
            <button class="quiet" type="submit">
                Search ↗
            </button>
        </form>
        <div class="search-options">
            <label>
                <input v-model="regex" type="checkbox"/>
                Regular expression
            </label>
            <span>Transcription-aware · stress and vowel marks optional</span>
        </div>
        <p v-if="regex" class="regex-help muted">
            For example: s[əe]m.* or \bbook\b. Matching ignores case.
        </p>
        <p v-if="pending" role="status" class="muted">
            Searching…
        </p>
        <p v-else-if="error" role="alert" class="error">
            {{ error }}
        </p>
        <template v-else-if="response">
            <p class="result-count muted" aria-live="polite">
                {{ response.total }} matches · up to 30 shown per group
            </p>
            <section v-for="group in groups" :key="group.type" class="result-group">
                <h3>
                    {{ group.label }}
                    <span class="muted">{{ response.counts[group.type] }}</span>
                </h3>
                <NuxtLink
                    v-for="result in group.results"
                    :key="result.id"
                    :to="result.to"
                    class="search-result"
                    @click="emit('navigate')"
                >
                    <span class="result-title">{{ result.title }}</span>
                    <MatchSnippet :text="result.snippet" :ranges="result.ranges"/>
                </NuxtLink>
            </section>
            <p v-if="!response.total" class="empty">
                No matches. Try a base form or a shorter phrase.
            </p>
        </template>
    </div>
</template>

<script setup lang="ts">
import { watchDebounced } from '@vueuse/core'
import type { ISearchResult } from '#shared/types/ISearchResult'

const props = defineProps<{ autofocus?: boolean
    initial?: string }>()
const emit = defineEmits<{ navigate: [] }>()
const inputId = useId()
const input = ref<HTMLInputElement | null>(null)
const query = ref(props.initial || '')
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
                    || 'Search failed.'
    }
    finally {
        if (current === requestId) pending.value = false
    }
}
watchDebounced([query, regex], run, { debounce: 300 })
onMounted(() => {
    if (props.autofocus) input.value?.focus()
    if (query.value) run()
})
const labels = {
    root: 'Roots',
    form: 'Attested forms',
    gloss: 'Senses & meanings',
    example: 'Glossary examples',
    text: 'Corpus passages',
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
    display: flex;
    gap: 0.5rem;
}
.search-form input {
    flex: 1;
    width: 100%;
    font-family: var(--font-serif);
    font-size: 1.4rem;
    padding: 0.7rem 1rem;
}
.search-options {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 0.4rem;
    margin: 0.6rem 0 1.2rem;
    color: var(--muted);
    font-size: 0.7rem;
}
.search-options label {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.regex-help {
    font-size: 0.75rem;
}
.result-count {
    font-size: 0.72rem;
    margin-bottom: 1.5rem;
}
.result-group {
    margin: 1.5rem 0;
}
.result-group h3 {
    font-size: 1.3rem;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 0.4rem;
}
.result-group h3 span {
    font-family: var(--font-sans);
    font-size: 0.65rem;
    margin-left: 0.6rem;
}
.search-result {
    display: grid;
    gap: 0.15rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--rule);
    text-decoration: none;
    color: var(--ink);
    font-size: 0.85rem;
}
.search-result:hover {
    background: var(--panel);
}
.result-title {
    color: var(--accent);
    font-size: 0.75rem;
}
</style>
