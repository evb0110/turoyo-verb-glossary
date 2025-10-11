<template>
    <UTable
        v-if="searchQuery.length >= 2"
        :columns="columns"
        :data="displayed"
        :loading="pending"
    >
        <template #root-cell="{ row }">
            <NuxtLink
                :to="`/verbs/${rootToSlug(row.original.root)}`"
                class="font-semibold text-primary hover:underline turoyo-text"
            >
                {{ row.original.root }}
            </NuxtLink>
        </template>

        <template #etymology_source-cell="{ row }">
            <span class="text-sm">{{ row.original.etymology_sources?.join(', ') || '—' }}</span>
        </template>

        <template #preview-cell="{ row }">
            <div v-if="verbDetails.has(row.original.root)" class="verb-preview">
                <template v-if="searchType === 'roots'">
                    <!-- Full article preview for "roots only" mode -->
                    <div
                        class="preview-content"
                        v-html="generateFullPreview(verbDetails.get(row.original.root)!)"
                    />
                </template>
                <template v-else>
                    <!-- Show excerpts for "everything" mode -->
                    <div class="preview-excerpts">
                        <div
                            v-for="(excerpt, i) in generateExcerpts(
                                verbDetails.get(row.original.root)!,
                                searchQuery,
                                { useRegex: regexMode === 'on', caseSensitive: caseParam === 'on', maxExcerpts: 5 }
                            )"
                            :key="i"
                            class="preview-excerpt"
                        >
                            <span class="excerpt-label">{{ excerpt.label }}</span>
                            <span class="excerpt-text" v-html="excerpt.html" />
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

const columns = [
    {
        accessorKey: 'root',
        header: 'Root',
        size: 150
    },
    {
        accessorKey: 'etymology_source',
        header: 'Etymology',
        size: 120
    },
    {
        accessorKey: 'preview',
        header: 'Article Preview'
    }
]
</script>
