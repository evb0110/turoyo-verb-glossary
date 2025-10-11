<template>
    <div v-if="searchQuery.length >= 2" class="flex flex-wrap items-center gap-3 pt-4 text-sm text-muted">
        <span>
            {{ displayedCount }} {{ displayedCount === 1 ? 'match' : 'matches' }}
        </span>
        <UBadge v-if="searchQuery.length" variant="soft">
            Query: {{ searchQuery }}
        </UBadge>
        <UBadge v-if="filters.letter" color="primary" variant="soft">
            Letter: {{ filters.letter }}
        </UBadge>
        <UBadge v-if="filters.etymology" color="success" variant="soft">
            Etymology: {{ filters.etymology }}
        </UBadge>
        <UBadge v-if="filters.stem" color="info" variant="soft">
            Stem: {{ filters.stem }}
        </UBadge>
    </div>
</template>

<script setup lang="ts">
import type { Filters } from '~/types/types/search'

defineProps<{
    searchQuery: string
    displayedCount: number
    filters: Filters
}>()
</script>
