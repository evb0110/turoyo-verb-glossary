<template>
    <div>
        <header class="page-heading">
            <p class="eyebrow">
                The text corpus
            </p>
            <h1>Voices behind the words</h1>
            <p>
                {{ texts.length }} texts, organised by collection. Reading status records whether
                agents have analysed the text’s verbs.
            </p>
        </header>
        <label class="sr-only" for="text-filter">Filter texts</label>
        <input
            id="text-filter"
            v-model="filter"
            placeholder="Find a text or collection…"
            class="text-filter"
        />
        <p v-if="error" class="error">
            Texts could not be loaded.
        </p>
        <section v-for="[collection, items] in collections" :key="collection" class="collection">
            <h2>
                {{ collection }}
                <span class="muted">{{ items.length }}</span>
            </h2>
            <NuxtLink
                v-for="text in items"
                :key="text.id"
                :to="`/texts/${encodeURIComponent(text.id)}`"
                class="text-row"
            >
                <span class="text-cite">{{ text.cite }}</span>
                <span class="text-title">{{ text.title
                }}<small v-if="text.speakerPlace">Speaker/place: {{ text.speakerPlace }}</small></span>
                <span class="text-meta">
                    {{ text.words.toLocaleString() }} words · {{ text.translated }}/{{
                        text.verses
                    }}
                    translated
                </span>
                <span class="pill" :class="{ read: text.reading === 'read' }">
                    {{
                        text.reading === 'read'
                            ? 'Read'
                            : text.reading === 'partial'
                                ? 'Partially read'
                                : 'Unread'
                    }}
                </span>
            </NuxtLink>
        </section>
        <p v-if="!collections.length" class="empty">
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
    max-width: 32rem;
    margin-bottom: 1rem;
}
.collection {
    margin-top: 2rem;
}
.collection h2 {
    border-bottom: 1px solid var(--rule);
    padding-bottom: 0.7rem;
}
.collection h2 span {
    font-size: 1rem;
    margin-left: 0.5rem;
}
.text-row {
    display: grid;
    grid-template-columns: 3rem 1fr auto auto;
    align-items: center;
    gap: 1rem;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--rule);
    text-decoration: none;
    color: var(--ink);
}
.text-cite {
    color: var(--muted);
    font-size: 0.8rem;
}
.text-title {
    font-family: var(--font-serif);
    font-size: 1.1rem;
}
.text-title small {
    display: block;
    font-family: var(--font-sans);
    font-size: 0.65rem;
    color: var(--muted);
}
.text-meta {
    color: var(--muted);
    font-size: 0.65rem;
}
.pill {
    color: var(--muted);
}
.pill.read {
    color: var(--accent);
}
@media (max-width: 1100px) {
    .text-row {
        grid-template-columns: 2.5rem 1fr auto;
        gap: 0.7rem;
    }
    .text-meta {
        grid-column: 2;
    }
    .text-row .pill {
        grid-column: 3;
        grid-row: span 2;
    }
}
@media (max-width: 500px) {
    .text-row {
        grid-template-columns: 2rem 1fr;
    }
    .text-row .pill {
        grid-column: 2;
        grid-row: auto;
        justify-self: start;
    }
}
</style>
