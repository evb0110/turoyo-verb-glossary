<template>
    <div class="space-y-6 py-4">
        <UCard>
            <div class="space-y-4">
                <SearchControls
                    v-model:query="q"
                    v-model:search-everything="searchEverything"
                    v-model:use-regex="useRegex"
                    v-model:case-sensitive="caseSensitive"
                    :placeholder="searchPlaceholder"
                    @search="performSearch"
                    @clear="clearSearch"
                    @show-help="showRegexHelp = true"
                />

                <div class="pt-2">
                    <VerbFilters
                        v-model:etymology="filterEtymology"
                        v-model:letter="filterLetter"
                        v-model:stem="filterStem"
                        :etymologies="etymologyOptions"
                        :letters="letterOptions"
                        :stems="stemOptions"
                        @reset="resetFilters"
                    />
                </div>

                <SearchResultsMetadata
                    :search-query="searchQuery"
                    :displayed-count="displayed.length"
                    :filters="filters"
                />

                <VerbSearchResults
                    :search-query="searchQuery"
                    :search-type="searchType"
                    :regex-mode="regexMode"
                    :case-param="caseParam"
                    :displayed="displayed"
                    :verb-previews="verbPreviews"
                    :pending="pending"
                />

                <div
                    v-if="searchQuery.length >= 2 && filtered.length === 0 && !pending"
                    class="rounded-lg border border-dashed px-4 py-6 text-center text-sm text-muted"
                >
                    No matches found. Try another keyword or broaden your search.
                </div>
            </div>
        </UCard>

        <RegexHelpModal v-model:open="showRegexHelp" />
    </div>
</template>

<script lang="ts" setup>
import { useRouteQuery } from '@vueuse/router'
import { generateLetterOptions, generateEtymologyOptions, generateStemOptions, applyFilters } from '~/utils/searchFilters'

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

interface VerbMetadata {
    root: string
    etymology_sources: string[]
    stems: string[]
}

const showRegexHelp = ref(false)

// Sync search state with URL query params
const q = useRouteQuery<string>('q', '')
const searchType = useRouteQuery<'roots' | 'all'>('type', 'roots')
const regexMode = useRouteQuery<'on' | 'off'>('regex', 'on')
const caseParam = useRouteQuery<'on' | 'off'>('case', 'off')
const filterLetter = useRouteQuery<string | null>('letter', null)
const filterEtymology = useRouteQuery<string | null>('etymology', null)
const filterStem = useRouteQuery<string | null>('stem', null)

// Derived state
const searchEverything = computed({
    get: () => searchType.value === 'all',
    set: (value) => { searchType.value = value ? 'all' : 'roots' }
})

const useRegex = computed({
    get: () => regexMode.value === 'on',
    set: (value) => { regexMode.value = value ? 'on' : 'off' }
})

const caseSensitive = computed({
    get: () => caseParam.value === 'on',
    set: (value) => { caseParam.value = value ? 'on' : 'off' }
})

const searchPlaceholder = computed(() => {
    if (regexMode.value === 'on') {
        return 'Regex search (use \\c for consonants, \\v for vowels)…'
    }
    return searchType.value === 'all'
        ? 'Search for roots, forms, translations, or etymology keywords…'
        : 'Search for verb roots…'
})

// Filters as computed getter for reactive access
const filters = computed(() => ({
    letter: filterLetter.value ?? null,
    etymology: filterEtymology.value ?? null,
    stem: filterStem.value ?? null
}))

// Initialize searchQuery from URL on mount, then sync with q
const searchQuery = ref(q.value)

// Single source of truth for search results - handles SSR and client-side searches
const { data: searchResults, pending } = await useAsyncData(
    // Unique key for cache invalidation
    () => `search-${searchQuery.value}-${searchType.value}-${regexMode.value}-${caseParam.value}`,
    async () => {
        if (!searchQuery.value || searchQuery.value.trim().length < 2) {
            return null
        }

        console.log(`[Search] Query: "${searchQuery.value}", type: ${searchType.value}`)

        return await $fetch<{
            total: number
            roots: string[]
            verbPreviews?: Record<string, VerbPreview>
            verbMetadata?: Record<string, VerbMetadata>
        }>('/api/verbs-fulltext-search', {
            method: 'POST',
            body: {
                query: searchQuery.value,
                useRegex: regexMode.value === 'on',
                caseSensitive: caseParam.value === 'on',
                searchType: searchType.value
            }
        })
    },
    {
        // Watch for changes and refetch automatically
        watch: [searchQuery, searchType, regexMode, caseParam]
    }
)

// Derive data from search results (computed for reactivity)
const verbPreviews = computed(() =>
    new Map(Object.entries(searchResults.value?.verbPreviews || {}))
)

const verbMetadata = computed(() =>
    new Map(Object.entries(searchResults.value?.verbMetadata || {}))
)

function performSearch() {
    searchQuery.value = q.value
}

function clearSearch() {
    q.value = ''
    searchQuery.value = ''
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

// Keep searchQuery in sync when q changes (e.g., via Cmd/Ctrl+K global search)
watch(q, (newQ) => {
    searchQuery.value = newQ
})

// Convert metadata to array for filter functions
const baseResults = computed(() => {
    if (!searchResults.value?.roots || searchResults.value.roots.length === 0) {
        return []
    }

    const metadata = verbMetadata.value
    return searchResults.value.roots
        .map(root => metadata.get(root))
        .filter((m): m is VerbMetadata => m !== undefined)
})

const letterOptions = computed(() => generateLetterOptions(baseResults.value))
const etymologyOptions = computed(() => generateEtymologyOptions(baseResults.value))
const stemOptions = computed(() => generateStemOptions(baseResults.value))

function resetFilters() {
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

const filtered = computed(() => {
    const result = baseResults.value
    if (result.length === 0) return []

    const applied = applyFilters(result, filters.value)
    console.log('[Index] Filtered result count:', applied.length)
    return applied
})

const displayed = computed(() => {
    const result = filtered.value
    console.log('[Index] Displayed count:', result.length)
    if (result.length > 0) {
        console.log('[Index] First displayed item:', result[0])
    }
    return result
})
</script>
