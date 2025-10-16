<template>
    <UTable
        v-if="searchQuery.length >= 2"
        :columns="columns"
        :data="displayed"
        :loading="pending"
        class="verb-results-table"
    >
        <template #root-cell="{ row }">
            <NuxtLink
                :to="getTo(row)"
                class="font-semibold text-primary hover:underline turoyo-text"
            >
                {{ row.original.root }}
            </NuxtLink>
        </template>

        <template #etymology_source-cell="{ row }">
            <span class="text-sm">
                {{ row.original.etymology_sources?.join(', ') || '—' }}
            </span>
        </template>

        <template #preview-cell="{ row }">
            <div class="py-4">
                <div v-if="pending" class="text-sm text-gray-400">
                    Loading...
                </div>
                <VerbPreview
                    v-else-if="row.original.verbPreview"
                    :verb="row.original.verbPreview"
                    class="max-h-64 px-4 overflow-y-auto"
                />
                <div
                    v-else-if="row.original.excerpts"
                    class="preview-excerpts space-y-2 max-h-64 px-4 overflow-y-auto"
                >
                    <div
                        v-for="(excerpt, i) in row.original.excerpts"
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
                <div v-else class="text-sm text-gray-400">
                    —
                </div>
            </div>
        </template>
    </UTable>
</template>

<script setup lang="ts">
import type { IVerbMetadataWithPreview } from '~/types/IVerbMetadataWithPreview'
import { rootToSlug } from '~/utils/rootToSlug'
import type { RouteLocationRaw } from '#vue-router'

interface TableRow {
    original: IVerbMetadataWithPreview
}

defineProps<{
    searchQuery: string
    displayed: IVerbMetadataWithPreview[]
    pending: boolean
    useRegex: boolean
    caseSensitive: boolean
}>()

const route = useRoute()

function getTo(row: TableRow): RouteLocationRaw {
    return {
        path: `/verbs/${rootToSlug(row.original.root)}`,
        query: route.query,
    }
}

const columns = [
    {
        accessorKey: 'root',
        header: 'Root',
    },
    {
        accessorKey: 'etymology_source',
        header: 'Etymology',
    },
    {
        accessorKey: 'preview',
        header: 'Article Preview',
        meta: {
            class: {
                td: 'p-0',
            },
        },
    },
]
</script>

<style>
.verb-results-table table {
    table-layout: fixed !important;
    width: 100% !important;
}

.verb-results-table th:nth-child(1),
.verb-results-table td:nth-child(1) {
    width: 100px !important;
    min-width: 100px !important;
    max-width: 100px !important;
}

.verb-results-table th:nth-child(2),
.verb-results-table td:nth-child(2) {
    width: 150px !important;
    min-width: 150px !important;
    max-width: 150px !important;
}

.verb-results-table th:nth-child(3),
.verb-results-table td:nth-child(3) {
    width: auto !important;
    min-width: 0 !important;
}

.verb-results-table td,
.verb-results-table th {
    overflow-wrap: break-word !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}
</style>
