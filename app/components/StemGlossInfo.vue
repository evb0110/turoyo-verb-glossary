<script lang="ts" setup>
import type { ITransformedStem } from '~/types/ITransformedStem'

defineProps<{
    stem: ITransformedStem
}>()
</script>

<template>
    <div class="prose max-w-none text-sm">
        <div class="font-semibold">
            {{ stem.stemLabel }}
        </div>
        <div v-if="stem.glossTokens.length">
            <span
                v-for="(t, i) in stem.glossTokens"
                :key="i"
                :class="{ italic: t.italic }"
            >
                {{ t.text }}
            </span>
        </div>
        <div v-else v-html="stem.label_raw"></div>
    </div>
</template>
