<script setup lang="ts">
import type { IExcerpt } from '~/types/IExcerpt'

defineProps<{
    excerpts: IExcerpt[]
    searchQuery: string
    useRegex: boolean
    caseSensitive: boolean
}>()
</script>

<template>
    <div class="preview-excerpts space-y-2 max-h-64 px-4 overflow-y-auto">
        <div
            v-for="(excerpt, i) in excerpts"
            :key="i"
            class="preview-excerpt"
        >
            <span
                class="excerpt-label block text-xs font-semibold text-gray-600 dark:text-gray-400"
            >
                {{ excerpt.label }}
            </span>
            <span class="excerpt-text block whitespace-normal break-words">
                <HighlightedText
                    :text="excerpt.text"
                    :query="searchQuery"
                    :use-regex="useRegex"
                    :case-sensitive="caseSensitive"
                />
            </span>
        </div>
    </div>
</template>
