<template>
    <div class="passage">
        <p class="small">
            <NuxtLink :to="verseHref(reference.textId, reference.v)">{{ reference.cite }}</NuxtLink>
            <span class="muted"> · {{ label }}<template v-if="data?.title"> · {{ data.title }}</template></span>
        </p>
        <p v-if="status === 'idle' || status === 'pending'" role="status" class="small muted">
            Loading text…
        </p>
        <p v-else-if="error" class="small muted">
            This text is unavailable. Please check the printed source.
        </p>
        <div v-else-if="verse" class="passage-text">
            <p class="tur">
                {{ verse.tur }}
            </p>
            <p>
                {{ verse.tr || "No translation available." }}
                <span v-if="data?.translationSource === 'machine'" class="muted small">(machine translation)</span>
            </p>
        </div>
        <p v-else class="small muted">
            The cited verse is not present in this text.
        </p>
    </div>
</template>

<script setup lang="ts">
import { verseHref } from '~/utils/verseHref'

const props = defineProps<{
    reference: { textId: string
        v: number
        cite: string }
    label: string
}>()
// Fetched in the browser only; "idle" on the server and "pending" while hydrating both show
// the loading line, so the server and client renders agree.
const {
    data,
    status,
    error,
} = useFetch(
    () => `/api/glossary/texts/${encodeURIComponent(props.reference.textId)}`,
    {
        query: computed(() => ({ v: props.reference.v })),
        lazy: true,
        server: false,
    }
)
const verse = computed(() => data.value?.verses.find(item => item.v === props.reference.v))
</script>

<style scoped>
.passage {
  display: grid;
  gap: 0.1rem;
}
.passage-text {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0 1.5rem;
}
@media (max-width: 760px) {
  .passage-text {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
