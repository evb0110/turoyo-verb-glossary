<script lang="ts" setup>
import { transformStemForDisplay } from '~/utils/transformStemForDisplay'
import type { IStem } from '#shared/types/IStem'

const { stem } = defineProps<{
    stem: IStem
}>()

const transformedStem = computed(() => transformStemForDisplay(stem))
</script>

<template>
    <div class="space-y-4 mb-8">
        <StemHeader :stem="transformedStem"/>
        <VerbStemTable :stem="transformedStem"/>
    </div>
</template>
