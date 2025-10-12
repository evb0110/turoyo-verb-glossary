<template>
    <div class="space-y-6 px-6 py-4">
        <UCard>
            <div class="space-y-4">
                <SearchControls
                    v-model:query="q"
                    v-model:search-everything="searchEverything"
                    v-model:use-regex="useRegex"
                    v-model:case-sensitive="caseSensitive"
                    :placeholder="getSearchPlaceholder()"
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
                    :loading-details="loadingDetails"
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
import type { Filters } from '~/types/types/search'
import type { VerbIndex } from '~/types/verb'
import { generateLetterOptions, generateEtymologyOptions, generateStemOptions, applyFilters } from '~/utils/searchFilters'

const { sessionStatus, isApproved } = useAuth()

// Client-side only: redirect to login if not authenticated
// NOTE: Don't use immediate:true to avoid triggering on hydration
if (import.meta.client) {
    watch(sessionStatus, (status) => {
        if (status === 'guest') {
            navigateTo('/login')
        }
    })
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

interface VerbMetadata {
    root: string
    etymology_sources: string[]
    stems: string[]
}

const { search } = useVerbSearch()

const pending = ref(false)
const showRegexHelp = ref(false)

// Store metadata from search results (instead of loading huge index!)
const verbMetadata = ref<Map<string, VerbMetadata>>(new Map())

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

function getSearchPlaceholder() {
    if (regexMode.value === 'on') {
        return 'Regex search (use \\c for consonants, \\v for vowels)…'
    }
    return searchType.value === 'all'
        ? 'Search for roots, forms, translations, or etymology keywords…'
        : 'Search for verb roots…'
}

// Filters as computed getter for reactive access
const filters = computed(() => ({
    letter: filterLetter.value ?? null,
    etymology: filterEtymology.value ?? null,
    stem: filterStem.value ?? null
}))

// Initialize searchQuery from URL on mount, then sync with q
const searchQuery = ref<string>(q.value)
const results = ref<string[]>([])

// Store pre-rendered HTML previews from server
const verbPreviews = ref<Map<string, VerbPreview>>(new Map())
const loadingDetails = ref(false)

// Perform initial search from URL during SSR
// Use unified search endpoint for both "roots only" and "everything" modes
if (searchQuery.value && searchQuery.value.trim().length >= 2) {
    const isUsingRegex = regexMode.value === 'on'
    const isCaseSensitive = caseParam.value === 'on'

    console.log(`[SSR] Searching with unified endpoint: "${searchQuery.value}"`)
    try {
        const response = await $fetch<{
            total: number
            roots: string[]
            verbPreviews?: Record<string, VerbPreview>
            verbMetadata?: Record<string, VerbMetadata>
        }>('/api/verbs-fulltext-search', {
            method: 'POST',
            body: {
                query: searchQuery.value,
                useRegex: isUsingRegex,
                caseSensitive: isCaseSensitive,
                searchType: searchType.value
            }
        })

        results.value = response.roots
        if (response.verbPreviews) {
            console.log(`[SSR] Got ${response.roots.length} results with previews`)
            verbPreviews.value = new Map(Object.entries(response.verbPreviews))
        }
        if (response.verbMetadata) {
            verbMetadata.value = new Map(Object.entries(response.verbMetadata))
        }
    }
    catch (e) {
        console.error('[SSR] Search failed:', e)
    }
}

function performSearch() {
    searchQuery.value = q.value
}

function clearSearch() {
    q.value = ''
    searchQuery.value = ''
    results.value = []
    verbPreviews.value.clear()
    verbMetadata.value.clear()
    filterLetter.value = null
    filterEtymology.value = null
    filterStem.value = null
}

async function runSearch(value: string) {
    const isUsingRegex = regexMode.value === 'on'
    const isCaseSensitive = caseParam.value === 'on'
    console.log('[Index] Run search:', value, 'mode:', searchType.value, 'regex:', isUsingRegex)

    if (!value || value.trim().length < 2) {
        console.log('[Index] Query too short, clearing results')
        results.value = []
        verbPreviews.value.clear()
        verbMetadata.value.clear()
        pending.value = false
        return
    }

    results.value = []
    verbPreviews.value.clear()
    verbMetadata.value.clear()
    pending.value = true

    // Use unified search endpoint for both modes
    try {
        const response = await $fetch<{
            total: number
            roots: string[]
            verbPreviews?: Record<string, VerbPreview>
            verbMetadata?: Record<string, VerbMetadata>
        }>('/api/verbs-fulltext-search', {
            method: 'POST',
            body: {
                query: value,
                useRegex: isUsingRegex,
                caseSensitive: isCaseSensitive,
                searchType: searchType.value
            }
        })

        results.value = response.roots
        if (response.verbPreviews) {
            console.log(`[Index] Got ${response.roots.length} results with previews`)
            verbPreviews.value = new Map(Object.entries(response.verbPreviews))
        }
        if (response.verbMetadata) {
            verbMetadata.value = new Map(Object.entries(response.verbMetadata))
        }
    }
    catch (e) {
        console.error('[Index] Search failed:', e)
    }
    finally {
        pending.value = false
    }
}

// Convert metadata map to VerbIndexEntry array for filter functions
const baseResults = computed(() => {
    if (!searchQuery.value || searchQuery.value.trim().length < 2 || results.value.length === 0) {
        return []
    }
    // Use metadata from search results instead of loading huge index
    return results.value
        .map(root => verbMetadata.value.get(root))
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

watch(
    [searchQuery, searchType, regexMode, caseParam],
    () => {
        runSearch(searchQuery.value)
    }
)

// Keep searchQuery in sync when q changes (e.g., via Cmd/Ctrl+K global search)
watch(q, (newQ) => {
    searchQuery.value = newQ
})

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

// No longer need to watch filtered - unified search endpoint returns previews directly!
</script>
