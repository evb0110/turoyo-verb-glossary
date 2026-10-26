<template>
    <div v-if="data" class="reader">
        <BackLink fallback="/texts" fallback-label="All texts"/>
        <header class="reader-head">
            <h1>{{ data.title || data.cite }}</h1>
            <p class="small muted">
                {{ data.collection }} · text {{ data.cite }}<template v-if="data.speakerPlace">
                    · speaker/place {{ data.speakerPlace }}
                </template>
                · {{ data.verses.length }} verses · {{ translationLabel }} ·
                {{ data.occurrences?.length ? `${data.occurrences.length} verbs analysed` : "verbs not analysed yet" }}
            </p>
            <p v-if="machine" class="machine small">
                The translation is a machine translation made for this project, not a published one.
            </p>
        </header>
        <p v-if="targetVerse !== null && !data.verses.some((verse) => verse.v === targetVerse)" class="error">
            Verse {{ targetVerse }} is not present in this text.
        </p>
        <div class="columns small muted" aria-hidden="true">
            <span></span>
            <span>{{ data.occurrences?.length ? "Turoyo: click an underlined verb for its analysis" : "Turoyo" }}</span>
            <span>{{ translationLabel }}</span>
        </div>
        <CorpusVerse
            v-for="verse in data.verses"
            :key="verse.v"
            :verse="verse"
            :occurrences="occurrences.get(verse.v) || []"
            :flags="flags.get(verse.v) || []"
            :selected="verse.v === targetVerse"
        />
    </div>
</template>

<script setup lang="ts">
import { onKeyStroke } from '@vueuse/core'
import type { IAlignment } from '#shared/types/IAlignment'
import type { IOccurrence } from '#shared/types/IOccurrence'

const route = useRoute()
const {
    data,
    error,
} = await useFetch(() => `/api/glossary/texts/${encodeURIComponent(String(route.params.id))}`)
if (error.value)
    throw createError({
        statusCode: error.value.statusCode || 500,
        statusMessage: 'Text could not be loaded.',
    })
const { selected } = useReaderVerb()
selected.value = null
onBeforeUnmount(() => {
    selected.value = null
})
onKeyStroke('Escape', () => {
    selected.value = null
})
// The scroll to ?v=N happens in router.options.ts, after the page has rendered.
const targetVerse = computed(() =>
    route.query.v !== undefined && Number.isSafeInteger(Number(route.query.v)) ? Number(route.query.v) : null
)
function byVerse<T extends { v: number }>(items: T[] | undefined) {
    const map = new Map<number, T[]>()
    for (const item of items || []) map.set(item.v, [...(map.get(item.v) || []), item])
    return map
}
const occurrences = computed(() => byVerse<IOccurrence>(data.value?.occurrences))
const flags = computed(() => byVerse<IAlignment>(data.value?.alignment))
const machine = computed(() => data.value?.translationSource === 'machine')
const translationLabel = computed(() => {
    const language = data.value?.lang === 'GERMAN' ? 'German' : data.value?.lang === 'ENGLISH' ? 'English' : ''
    if (!language) return 'No translation available'
    return machine.value ? `${language} translation (machine, made for this project)` : `${language} translation`
})
useHead({ title: computed(() => data.value?.title || data.value?.cite || 'Text') })
</script>

<style scoped>
.reader-head {
  display: grid;
  gap: 0.15rem;
  margin-bottom: 0.75rem;
}
.machine {
  color: var(--correction);
  font-weight: 600;
}
.columns {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1.1fr) minmax(0, 1fr);
  gap: 0 1.5rem;
  padding: 0.2rem 0;
}
@media (max-width: 760px) {
  .columns {
    display: none;
  }
}
</style>
