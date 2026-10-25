<template>
    <div>
        <header class="page-heading">
            <h1>Glossary</h1>
            <p>Look up a Turoyo verb, or browse the roots below.</p>
        </header>
        <SearchExplorer v-model="query"/>
        <template v-if="!query.trim()">
            <nav class="letters" aria-label="Jump to a letter">
                <a
                    v-for="[letter] in groups"
                    :key="letter"
                    :href="`#letter-${encodeURIComponent(letter)}`"
                >{{ letter }}</a>
            </nav>
            <section
                v-for="[letter, items] in groups"
                :id="`letter-${letter}`"
                :key="letter"
                class="letter-group"
            >
                <h2>{{ letter }}</h2>
                <NuxtLink
                    v-for="root in items"
                    :key="root.id"
                    :to="entryHref(root.id)"
                    class="root-row"
                ><span>{{ root.root }}</span><span class="gloss">{{ root.proposed ? "Suggested new verb · " : ""
                }}{{ root.glossPreview }}</span><span aria-hidden="true">→</span></NuxtLink>
            </section>
        </template>
        <p v-if="error" class="error">
            The glossary could not be loaded. Please try again.
        </p>
    </div>
</template>

<script setup lang="ts">
import { entryHref } from '#shared/utils/entryHref'

const route = useRoute()
const router = useRouter()
const query = ref(String(route.query.q || ''))
watch(query, value => router.replace({ query: value ? { q: value } : {} }))
watch(
    () => route.query.q,
    (value) => {
        query.value = String(value || '')
    }
)
const {
    data,
    error,
} = await useFetch('/api/glossary/roots')
const groups = computed(() => {
    const map = new Map<string, NonNullable<typeof data.value>>()
    for (const root of data.value || []) {
        const letter = [...root.root][0] || '?'
        const rows = map.get(letter) || []
        rows.push(root)
        map.set(letter, rows)
    }
    return [...map.entries()]
})
useHead({ title: 'Glossary' })
</script>

<style scoped>
.letters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin: 1rem 0 2rem;
}
.letters a {
  min-width: 48px;
  min-height: 48px;
  display: grid;
  place-content: center;
  border: 1px solid var(--rule);
  border-radius: 5px;
  font-family: var(--font-serif);
  font-size: 1.35rem;
}
.letter-group {
  margin-top: 2rem;
}
.letter-group h2 {
  border-bottom: 2px solid var(--ink);
  padding-bottom: 0.4rem;
}
.root-row {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr) auto;
  align-items: baseline;
  gap: 0.6rem;
  padding: 1rem 0.25rem;
  border-bottom: 1px solid var(--rule);
  text-decoration: none;
  font-family: var(--font-serif);
  font-size: 1.5rem;
}
.gloss {
  font-family: var(--font-sans);
  font-size: 1rem;
  color: var(--ink);
}
</style>
