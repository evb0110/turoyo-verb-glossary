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
                <div v-else-if="hasAnyPreviews" class="max-h-64 px-4 overflow-y-auto">
                    <template v-if="searchType === 'roots' && verbPreviews.get(row.original.root)?.preview">
                        <div
                            class="preview-content whitespace-normal break-words"
                            v-html="verbPreviews.get(row.original.root)!.preview"
                        />
                    </template>
                    <template v-else-if="verbPreviews.get(row.original.root)?.excerpts">
                        <div class="preview-excerpts space-y-2">
                            <div
                                v-for="(excerpt, i) in verbPreviews.get(row.original.root)!.excerpts"
                                :key="i"
                                class="preview-excerpt"
                            >
                                <span class="excerpt-label block text-xs font-semibold text-gray-600 dark:text-gray-400">
                                    {{ excerpt.label }}
                                </span>
                                <span class="excerpt-text block whitespace-normal break-words" v-html="excerpt.html" />
                            </div>
                        </div>
                    </template>
                </div>
                <div v-else class="text-sm text-gray-400">
                    —
                </div>
            </div>
        </template>
    </UTable>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from '#vue-router'
import { rootToSlug } from '~/utils/slugify'

interface VerbMetadata {
    root: string
    etymology_sources: string[]
    stems: string[]
}

interface Excerpt {
    type: 'form' | 'example' | 'translation' | 'etymology' | 'gloss'
    stem?: string
    conjugationType?: string
    text: string
    html: string
    label: string
}

interface VerbPreview {
    excerpts?: Excerpt[]
    preview?: string
}

interface TableRow {
    original: VerbMetadata
}

const props = defineProps<{
    searchQuery: string
    searchType: 'roots' | 'all'
    displayed: VerbMetadata[]
    verbPreviews: Map<string, VerbPreview>
    pending: boolean
}>()

const route = useRoute()

function getTo(row: TableRow): RouteLocationRaw {
    return {
        path: `/verbs/${rootToSlug(row.original.root)}`,
        query: route.query
    }
}

const hasAnyPreviews = computed(() => props.verbPreviews.size > 0)

const columns = [
    {
        accessorKey: 'root',
        header: 'Root'
    },
    {
        accessorKey: 'etymology_source',
        header: 'Etymology'
    },
    {
        accessorKey: 'preview',
        header: 'Article Preview',
        meta: {
            class: {
                td: 'p-0'
            }
        }
    }
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
