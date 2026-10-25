<template>
    <div>
        <header class="page-heading">
            <p class="eyebrow">
                Reader’s notebook
            </p>
            <h1>Questions worth following</h1>
            <p>
                Observations from the corpus readers, grouped by research question. Each
                note leads back to the verse that prompted it.
            </p>
        </header>
        <label for="rq-filter" class="eyebrow">Research question</label>
        <select id="rq-filter" v-model="filter">
            <option value="">
                All questions
            </option>
            <option v-for="tag in tags" :key="tag">
                {{ tag }}
            </option>
        </select>
        <p v-if="error" class="error">
            Research notes could not be loaded.
        </p>
        <article v-for="note in filtered" :key="note.id" class="research-note">
            <div class="row">
                <span v-for="tag in note.occurrence.rq" :key="tag" class="pill">
                    {{ tag }}
                </span>
                <button
                    class="verse-link"
                    @click="open(note.textId, note.occurrence.v, note.cite)"
                >
                    {{ note.cite }} ↗
                </button>
            </div>
            <h3>
                {{ note.occurrence.root }}
                <span class="turoyo">{{ note.occurrence.form }}</span>
            </h3>
            <p class="serif">
                {{ note.occurrence.observations || note.occurrence.meaning }}
            </p>
            <p class="muted meaning">
                {{ note.occurrence.meaning }} · {{ note.occurrence.arguments }}
            </p>
            <div class="row note-links">
                <NuxtLink
                    v-if="note.occurrence.entryId"
                    :to="
                        entryHref(
                            note.occurrence.entryId,
                            `${note.occurrence.entryId}.${note.occurrence.stem}`,
                            note.occurrence.sense
                        )
                    "
                >
                    Dictionary entry ↗
                </NuxtLink>
                <NuxtLink :to="`/texts/${note.textId}?v=${note.occurrence.v}`">
                    {{ note.title }} ↗
                </NuxtLink>
            </div>
        </article>
        <p v-if="!filtered.length" class="empty">
            No tagged observations yet. They will appear as the corpus reading progresses.
        </p>
    </div>
</template>

<script setup lang="ts">
import { entryHref } from '#shared/utils/entryHref'

const {
    data,
    error,
} = await useFetch('/api/glossary/research')
const { open } = useEvidence()
const filter = ref('')
const tags = computed(() =>
    [...new Set((data.value || []).flatMap(note => note.occurrence.rq))].sort()
)
const filtered = computed(() =>
    (data.value || []).filter(
        note => !filter.value || note.occurrence.rq.includes(filter.value)
    )
)
useHead({ title: 'Research notes' })
</script>

<style scoped>
select {
    display: block;
    margin: 0.6rem 0 2rem;
    width: 100%;
    max-width: 30rem;
}
.research-note {
    border-top: 1px solid var(--rule);
    padding: 1.5rem 0;
}
.research-note .pill {
    color: var(--note);
}
.verse-link {
    margin-left: auto;
    color: var(--accent);
    font-size: .889rem;
}
.research-note h3 {
    margin: 1rem 0 0.5rem;
}
.research-note h3 span {
    margin-left: 0.7rem;
    color: var(--muted);
}
.research-note > .serif {
    font-size: 1.25rem;
}
.meaning {
    font-size: .889rem;
    margin: 0.6rem 0;
}
.note-links {
    font-size: .889rem;
    margin-top: 1rem;
}
</style>
