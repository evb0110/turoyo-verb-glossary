<script lang="ts" setup>
import { transformStemForDisplay } from '~/utils/transformStemForDisplay'
import type { IStem } from '#shared/types/IStem'

const { stem } = defineProps<{
    stem: IStem
}>()

const transformedStem = computed(() => transformStemForDisplay(stem))
</script>

<template>
    <UCard
        :ui="{ body: 'space-y-4' }"
        class="border border-transparent transition hover:border-primary/40"
    >
        <StemHeader :stem="transformedStem"/>
        <StemExamples :stem="transformedStem"/>
    </UCard>
</template>
