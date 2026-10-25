<template>
    <div>
        <header class="page-heading">
            <h1>Texts</h1>
            <p>Read Turoyo texts and their translations, grouped by collection.</p>
        </header>
        <label for="text-filter">Find a text or collection</label><input
            id="text-filter"
            v-model="filter"
            type="search"
            placeholder="Title, speaker or place"
            class="text-filter"
        />
        <p v-if="error" class="error">
            Texts could not be loaded. Please try again.
        </p>
        <section
            v-for="[collection, items] in collections"
            :key="collection"
            class="collection"
        >
            <h2>{{ collection }}</h2>
            <NuxtLink
                v-for="text in items"
                :key="text.id"
                :to="`/texts/${encodeURIComponent(text.id)}`"
                class="text-row"
            ><span class="caption">{{ text.cite }}</span><span class="text-title serif">{{ text.title }}</span><span
                v-if="text.speakerPlace"
                class="caption"
            >Speaker/place: {{ text.speakerPlace }}</span><span class="analysis-status">{{
                text.reading === "read"
                    ? "Verbs analysed"
                    : text.reading === "partial"
                        ? "Some verbs analysed"
                        : "Not analysed yet"
            }}</span></NuxtLink>
        </section>
        <p v-if="!collections.length && !error" class="empty">
            No matching texts.
        </p>
    </div>
</template>

<script setup lang="ts">
const {
    data,
    error,
} = await useFetch('/api/glossary/texts')
const texts = computed(() => data.value || [])
const filter = ref('')
const collections = computed(() => {
    const groups = new Map<string, typeof texts.value>()
    for (const text of texts.value) {
        if (
            !`${text.title} ${text.speakerPlace || ''} ${text.collection} ${text.id} ${text.cite}`
                .toLowerCase()
                .includes(filter.value.toLowerCase())
        )
            continue
        const items = groups.get(text.collection) || []
        items.push(text)
        groups.set(text.collection, items)
    }
    return [...groups.entries()]
})
useHead({ title: 'Texts' })
</script>

<style scoped>
.text-filter {
  width: 100%;
  margin-top: 0.6rem;
}
.collection {
  margin-top: 2rem;
}
.collection h2 {
  padding-bottom: 0.7rem;
  border-bottom: 2px solid var(--ink);
}
.text-row {
  display: grid;
  gap: 0.3rem;
  padding: 1.1rem 0;
  border-bottom: 1px solid var(--rule);
  color: var(--ink);
  text-decoration: none;
}
.text-title {
  font-size: 1.4rem;
}
.analysis-status {
  font-size: 0.889rem;
  color: var(--accent);
}
</style>
