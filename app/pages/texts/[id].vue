<template>
    <div v-if="data">
        <header class="page-heading">
            <NuxtLink to="/texts" class="back-link">← Texts</NuxtLink>
            <p class="caption">
                {{ data.collection }} · {{ data.cite }}
            </p>
            <h1>{{ data.title }}</h1>
            <p v-if="data.speakerPlace">
                Speaker/place: {{ data.speakerPlace }}
            </p>
            <p class="caption">
                {{
                    data.lang === "GERMAN"
                        ? "German translation"
                        : data.lang === "ENGLISH"
                            ? "English translation"
                            : "No translation available"
                }}
                · {{ data.occurrences?.length ? "Verbs analysed" : "Not analysed yet" }}
            </p>
        </header>
        <p class="reader-instruction">
            Tap an underlined verb to see its meaning and open the glossary entry.
        </p>
        <CorpusVerse
            v-for="verse in data.verses"
            :key="verse.v"
            :verse="verse"
            :occurrences="
                (data.occurrences || []).filter((item) => item.v === verse.v)
            "
            :flags="(data.alignment || []).filter((item) => item.v === verse.v)"
            :selected="verse.v === targetVerse"
        />
        <p
            v-if="
                targetVerse !== null
                    && !data.verses.some((verse) => verse.v === targetVerse)
            "
            class="error"
        >
            Verse {{ targetVerse }} is not present in this text.
        </p>
        <UModal
            :open="!!selected"
            :title="
                selected
                    ? `${selected.verb.root} · Stem ${selected.verb.stem}`
                    : 'Verb meaning'
            "
            description="Meaning of this verb in the text"
            :ui="{
                content:
                    'max-sm:bottom-0 max-sm:top-auto max-sm:translate-y-0 max-sm:rounded-b-none'
            }"
            @update:open="
                (value) => {
                    if (!value) selected = null;
                }
            "
        >
            <template #body>
                <div v-if="selected" class="stack verb-panel">
                    <p class="turoyo">
                        {{ selected.verb.form }}
                    </p>
                    <p>{{ selected.verb.meaning }}</p>
                    <NuxtLink
                        v-if="selected.verb.entryId"
                        class="primary"
                        :to="
                            entryHref(
                                selected.verb.entryId,
                                `${selected.verb.entryId}.${selected.verb.stem}`,
                                selected.verb.sense
                            )
                        "
                        @click="selected = null"
                    >Open glossary entry →</NuxtLink>
                    <p v-else>
                        This verb is not in the glossary yet.
                    </p>
                    <button class="quiet" @click="selected = null">
                        Close
                    </button>
                </div>
            </template>
        </UModal>
    </div>
</template>

<script setup lang="ts">
import { entryHref } from '#shared/utils/entryHref'

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
const { selected } = useReaderVerb()
selected.value = null
onBeforeUnmount(() => {
    selected.value = null
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
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  margin-bottom: 0.7rem;
}
.page-heading h1 {
  margin-top: 0.6rem;
}
.reader-instruction {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--rule);
}
.verb-panel {
  font-size: 1rem;
}
</style>
