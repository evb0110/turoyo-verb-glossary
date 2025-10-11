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
            <div v-if="verbDetails.has(row.original.root)" class="max-h-64 overflow-y-auto">
                <template v-if="searchType === 'roots'">
                    <!-- Full article preview for "roots only" mode -->
                    <div
                        class="preview-content whitespace-normal break-words"
                        v-html="generateFullPreview(verbDetails.get(row.original.root)!)"
                    />
                </template>
                <template v-else>
                    <!-- Show excerpts for "everything" mode -->
                    <div class="preview-excerpts space-y-2">
                        <div
                            v-for="(excerpt, i) in generateExcerpts(
                                verbDetails.get(row.original.root)!,
                                searchQuery,
                                { useRegex: regexMode === 'on', caseSensitive: caseParam === 'on', maxExcerpts: 5 }
                            )"
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
import type { Verb, VerbIndexEntry } from '~/types/verb'
import { generateExcerpts } from '~/utils/verbExcerpts'
import { generateFullPreview } from '~/utils/verbHtmlPreview'

const { rootToSlug } = useVerbs()

defineProps<{
    searchQuery: string
    searchType: 'roots' | 'all'
    regexMode: 'on' | 'off'
    caseParam: 'on' | 'off'
    displayed: VerbIndexEntry[]
    verbDetails: Map<string, Verb>
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
