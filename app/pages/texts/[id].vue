<template>
    <div v-if="data">
        <header class="page-heading">
            <NuxtLink to="/texts" class="back-link">← Text corpus</NuxtLink>
            <p class="eyebrow">
                {{ data.collection }} · {{ data.cite }}
            </p>
            <h1>{{ data.title }}</h1>
            <p v-if="data.speakerPlace" class="speaker-place">
                Speaker/place: {{ data.speakerPlace }}
            </p>
            <p>
                {{ data.verses.length }} verses ·
                {{
                    data.lang
                        ? `${data.lang === 'GERMAN' ? 'German' : 'English'} translation`
                        : 'Untranslated'
                }}
                ·
                {{
                    data.occurrences === undefined
                        ? 'Awaiting agent reading'
                        : `${data.occurrences.length} analysed occurrences`
                }}
            </p>
        </header>
        <div class="reader-legend">
            <span>Solid underline · analysed verb</span>
            <span class="suggested-key">Dashed underline · suggested addition</span>
            <span class="proposed-key">Double underline · linked proposal</span>
            <span>Hover for analysis · tap to inspect · open the linked sense</span>
        </div>
        <div class="reader-head">
            <span></span>
            <span>Ṭuroyo</span>
            <span>Translation</span>
        </div>
        <CorpusVerse
            v-for="verse in data.verses"
            :key="verse.v"
            :verse="verse"
            :occurrences="(data.occurrences || []).filter((item) => item.v === verse.v)"
            :flags="(data.alignment || []).filter((item) => item.v === verse.v)"
            :selected="verse.v === targetVerse"
        />
        <p
            v-if="targetVerse !== null && !data.verses.some((verse) => verse.v === targetVerse)"
            class="error"
        >
            Verse {{ targetVerse }} is not present in this text.
        </p>
    </div>
</template>

<script setup lang="ts">
const route = useRoute()
const {
    data,
    error,
} = await useFetch(
    () => `/api/glossary/texts/${encodeURIComponent(String(route.params.id))}`
)
if (error.value)
    throw createError({
        statusCode: error.value.statusCode || 500,
        statusMessage: 'Text could not be loaded.',
    })
const targetVerse = computed(() =>
    route.query.v !== undefined && Number.isSafeInteger(Number(route.query.v))
        ? Number(route.query.v)
        : null
)
function scrollToVerse() {
    if (targetVerse.value !== null)
        nextTick(() =>
            document
                .getElementById(`verse-${targetVerse.value}`)
                ?.scrollIntoView({ block: 'center' })
        )
}
onMounted(scrollToVerse)
watch(targetVerse, scrollToVerse)
useHead({ title: computed(() => data.value?.title || 'Text') })
</script>

<style scoped>
.back-link {
    font-size: 0.75rem;
    display: inline-block;
    margin-bottom: 1.5rem;
}
.page-heading h1 {
    font-size: clamp(2rem, 4vw, 3.2rem);
    max-width: 55rem;
}
.reader-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1.5rem;
    color: var(--accent);
    font-size: 0.65rem;
    margin-bottom: 1.5rem;
}
.proposed-key {
    color: var(--note);
}
.suggested-key {
    color: var(--correction);
}
.reader-head {
    display: grid;
    grid-template-columns: 2rem 1fr 1fr;
    gap: 1.5rem;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid var(--rule);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
}
@media (max-width: 680px) {
    .reader-head {
        display: none;
    }
}
</style>
