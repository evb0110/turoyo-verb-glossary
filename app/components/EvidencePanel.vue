<template>
    <USlideover
        :open="!!selected"
        :title="`Verse ${selected?.cite || ''}`"
        description="Evidence in context · three verses on either side"
        @update:open="
            (value) => {
                if (!value) selected = null
            }
        "
    >
        <template #body>
            <p v-if="pending" class="muted">
                Loading text…
            </p>
            <p v-else-if="error" class="error">
                This text could not be loaded.
            </p>
            <template v-else-if="data">
                <p class="eyebrow">
                    {{ data.collection }}
                </p>
                <h3>{{ data.title }}</h3>
                <p v-if="data.speakerPlace" class="muted">
                    Speaker/place: {{ data.speakerPlace }}
                </p>
                <div
                    v-for="verse in data.verses"
                    :key="verse.v"
                    class="context-verse"
                    :class="{ 'selected-verse': verse.v === selected?.v }"
                >
                    <span class="eyebrow">{{ data.cite }}/{{ verse.v }}</span>
                    <p class="turoyo">
                        {{ verse.tur }}
                    </p>
                    <p>{{ verse.tr || 'No translation available.' }}</p>
                </div>
                <p
                    v-if="!data.verses.some((verse) => verse.v === selected?.v)"
                    class="error"
                >
                    The cited verse is not present in this text.
                </p>
                <NuxtLink
                    :to="`/texts/${data.id}?v=${selected?.v}`"
                    class="quiet"
                    @click="selected = null"
                >
                    Read the full text ↗
                </NuxtLink>
            </template>
        </template>
    </USlideover>
</template>

<script setup lang="ts">
const { selected } = useEvidence()
const {
    data,
    pending,
    error,
} = await useFetch(
    () => `/api/glossary/texts/${encodeURIComponent(selected.value?.textId || '')}`,
    {
        query: computed(() => ({ v: selected.value?.v })),
        lazy: true,
    }
)
</script>

<style scoped>
.context-verse {
    border-top: 1px solid var(--rule);
    padding: 1rem;
    margin: 0.7rem 0;
}
.context-verse p {
    margin-top: 0.4rem;
}
.selected-verse {
    background: var(--panel);
    border-left: 3px solid var(--accent);
}
</style>
