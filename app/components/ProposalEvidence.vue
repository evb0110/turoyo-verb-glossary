<template>
    <section class="evidence-verse stack">
        <p class="caption">
            {{ label }} · {{ reference.cite }}
        </p>
        <p v-if="pending" role="status">
            Loading text…
        </p>
        <p v-else-if="error" class="muted">
            This text is unavailable. Please check the printed source.
        </p>
        <template v-else-if="verse">
            <p class="turoyo">
                {{ verse.tur }}
            </p>
            <p class="serif translation">
                {{ verse.tr || "No translation available." }}
            </p>
            <NuxtLink
                :to="`/texts/${encodeURIComponent(reference.textId)}?v=${reference.v}`"
            >Open the text at {{ reference.cite }} →</NuxtLink>
        </template>
        <p v-else class="muted">
            The cited verse is not present in this text.
        </p>
    </section>
</template>

<script setup lang="ts">
const props = defineProps<{
    reference: { textId: string
        v: number
        cite: string }
    label: string
}>()
const {
    data,
    pending,
    error,
} = await useFetch(
    () => `/api/glossary/texts/${encodeURIComponent(props.reference.textId)}`,
    {
        query: computed(() => ({ v: props.reference.v })),
        lazy: true,
    }
)
const verse = computed(() =>
    data.value?.verses.find(item => item.v === props.reference.v)
)
</script>

<style scoped>
.evidence-verse {
  border-left: 2px solid var(--rule);
  padding: 0.3rem 0 0.3rem 1rem;
  gap: 0.6rem;
}
.translation {
  font-size: 1.2rem;
}
.evidence-verse a {
  display: inline-flex;
  align-items: center;
  min-height: 48px;
}
</style>
