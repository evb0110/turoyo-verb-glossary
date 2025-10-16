<template>
    <span>
        <template v-for="(segment, i) in segments" :key="i">
            <mark v-if="segment.isMatch" class="highlight-match">{{ segment.text }}</mark>
            <template v-else>{{ segment.text }}</template>
        </template>
    </span>
</template>

<script setup lang="ts">
import { parseHighlights } from '~/utils/highlightText'

const props = withDefaults(
    defineProps<{
        text: string
        query: string
        useRegex?: boolean
        caseSensitive?: boolean
    }>(),
    {
        useRegex: false,
        caseSensitive: false
    }
)

const segments = computed(() => {
    return parseHighlights(props.text, props.query, {
        useRegex: props.useRegex,
        caseSensitive: props.caseSensitive
    })
})
</script>
