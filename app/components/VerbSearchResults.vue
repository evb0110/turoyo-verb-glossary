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
                :to="{ path: `/verbs/${rootToSlug(row.original.root)}`, query: route.query }"
                class="font-semibold text-primary hover:underline turoyo-text"
            >
                {{ row.original.root }}
            </NuxtLink>
        </template>

        <template #etymology_source-cell="{ row }">
            <span class="text-sm">{{ row.original.etymology_sources?.join(', ') || '—' }}</span>
        </template>

        <template #preview-cell="{ row }">
            <div v-if="verbPreviews.has(row.original.root)" class="max-h-64 overflow-y-auto">
                <template v-if="searchType === 'roots' && verbPreviews.get(row.original.root)?.preview">
                    <!-- Pre-rendered full article preview for "roots only" mode -->
                    <div
                        class="preview-content whitespace-normal break-words"
                        v-html="verbPreviews.get(row.original.root)!.preview"
                    />
                </template>
                <template v-else-if="verbPreviews.get(row.original.root)?.excerpts">
                    <!-- Pre-rendered excerpts for "everything" mode -->
                    <div class="preview-excerpts space-y-2">
                        <div
                            v-for="(excerpt, i) in verbPreviews.get(row.original.root)!.excerpts"
                            :key="i"
                            class="preview-excerpt"
                        >
                            <span class="excerpt-label block text-xs font-semibold text-gray-600 dark:text-gray-400">{{ excerpt.label }}</span>
                            <span class="excerpt-text block whitespace-normal break-words" v-html="excerpt.html" />
                        </div>
                    </div>
                </template>
            </div>
            <div v-else class="text-sm text-gray-400">
                {{ loadingDetails ? 'Loading...' : '—' }}
            </div>
        </template>
    </UTable>
</template>

<script setup lang="ts">
// Minimal metadata needed for display
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

const { rootToSlug } = useVerbs()

defineProps<{
    searchQuery: string
    searchType: 'roots' | 'all'
    regexMode: 'on' | 'off'
    caseParam: 'on' | 'off'
    displayed: VerbMetadata[]
    verbPreviews: Map<string, VerbPreview>
    loadingDetails: boolean
    pending: boolean
}>()

const route = useRoute()
watchEffect(() => {
    console.log(route?.query)
})

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
        header: 'Article Preview'
    }
]
</script>

<style>
/* Use global styles for table layout (scoped styles don't work well with :deep()) */
.verb-results-table table {
    table-layout: fixed !important;
    width: 100% !important;
}

/* Root column - fixed width */
.verb-results-table th:nth-child(1),
.verb-results-table td:nth-child(1) {
    width: 100px !important;
    min-width: 100px !important;
    max-width: 100px !important;
}

/* Etymology column - fixed width */
.verb-results-table th:nth-child(2),
.verb-results-table td:nth-child(2) {
    width: 150px !important;
    min-width: 150px !important;
    max-width: 150px !important;
}

/* Preview column - takes remaining space */
.verb-results-table th:nth-child(3),
.verb-results-table td:nth-child(3) {
    width: auto !important;
    min-width: 0 !important;
}

/* Ensure all cells wrap content */
.verb-results-table td,
.verb-results-table th {
    overflow-wrap: break-word !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}
</style>
